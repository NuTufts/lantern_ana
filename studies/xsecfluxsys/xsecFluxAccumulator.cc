
#include "xsecFluxAccumulator.h"
#include <iostream>
#include <stdexcept>
#include <algorithm>
#include "TKey.h"
#include "TDirectory.h"

XsecFluxAccumulator::XsecFluxAccumulator()
    : numVariables_(0),
      maxVariations_(0),
      maxValidWeight_(1000.0),
      configured_(false),
      missingEventCount_(0)
{
}

XsecFluxAccumulator::~XsecFluxAccumulator()
{
}

void XsecFluxAccumulator::configure(int numVariables,
                                     const std::vector<int>& binsPerVariable,
                                     const std::vector<std::string>& paramNames,
				     const std::vector<std::string>& xsecParams,
                                     int maxVariations,
                                     double maxValidWeight)
{
    numVariables_ = numVariables;
    binsPerVariable_ = binsPerVariable;
    maxVariations_ = maxVariations;
    maxValidWeight_ = maxValidWeight;

    includedParams_.clear();
    for (const auto& p : paramNames) {
        includedParams_.insert(p);
    }

    // Initialize bad weight counter
    badWeightsPerUniverse_.assign(maxVariations, 0);

    for ( auto const& xsecparname : xsecParams ) {
      xsecParamNames_[xsecparname] = 1;
    }

    // Clear any existing arrays
    arrays_.clear();
    variationsPerParam_.clear();
    missingEventCount_ = 0;

    configured_ = true;
    std::cout << "XsecFluxAccumulator configured: "
              << numVariables << " variables, "
              << paramNames.size() << " parameters, "
              << maxVariations << " max variations" << std::endl;
}

void XsecFluxAccumulator::reset()
{
    for (auto& kv : arrays_) {
        std::fill(kv.second.begin(), kv.second.end(), 0.0);
    }
    std::fill(badWeightsPerUniverse_.begin(), badWeightsPerUniverse_.end(), 0);

    // for (int varIdx=0; varIdx<numVariables_; varIdx++) {
    //   std::fill( badWeightsPerVariableBins_[varIdx].begin(), badWeightsPerVariableBins_[varIdx].end(), 0 );
    // }
    for ( auto& kv : badWeightsPerVariableBins_ ) {
      std::fill(kv.second.begin(), kv.second.end(), 0);
    }

    missingEventCount_ = 0;
}

TTree* XsecFluxAccumulator::findTreeInFile(TFile* file, const std::string& treeName)
{
    // First try direct access
    TTree* tree = dynamic_cast<TTree*>(file->Get(treeName.c_str()));
    if (tree) return tree;

    // Search in TDirectoryFiles
    TIter next(file->GetListOfKeys());
    TKey* key;
    while ((key = dynamic_cast<TKey*>(next()))) {
        TObject* obj = key->ReadObj();
        if (obj->InheritsFrom("TDirectoryFile")) {
            TDirectory* dir = dynamic_cast<TDirectory*>(obj);
            tree = dynamic_cast<TTree*>(dir->Get(treeName.c_str()));
            if (tree) return tree;
        }
    }
    return nullptr;
}

int XsecFluxAccumulator::processAllEvents(
    const std::string& weightFilePath,
    const std::string& weightTreeName,
    const std::string& weightBranchName,
    const std::string& runBranch,
    const std::string& subrunBranch,
    const std::string& eventBranch,
    const std::vector<std::vector<int>>& rseList,
    const std::vector<std::vector<int>>& binIndicesList,
    const std::vector<double>& centralWeights)
{
    if (!configured_) {
        throw std::runtime_error("XsecFluxAccumulator not configured. Call configure() first.");
    }

    size_t numEvents = rseList.size();
    if (numEvents == 0) {
        std::cout << "XsecFluxAccumulator: No events to process." << std::endl;
        return 0;
    }

    if (binIndicesList.size() != numEvents || centralWeights.size() != numEvents) {
        throw std::runtime_error("Mismatch in input vector sizes");
    }

    std::cout << "XsecFluxAccumulator: Processing " << numEvents << " events from "
              << weightFilePath << std::endl;

    // Open weight file
    TFile* weightFile = TFile::Open(weightFilePath.c_str(), "READ");
    if (!weightFile || weightFile->IsZombie()) {
        throw std::runtime_error("Failed to open weight file: " + weightFilePath);
    }

    // Find weight tree
    TTree* weightTree = findTreeInFile(weightFile, weightTreeName);
    if (!weightTree) {
        weightFile->Close();
        throw std::runtime_error("Failed to find tree " + weightTreeName + " in " + weightFilePath);
    }

    // Get number of entries in weight tree
    Long64_t nWeightEntries = weightTree->GetEntries();
    std::cout << "  Weight tree has " << nWeightEntries << " entries" << std::endl;

    // Set up branches for RSE lookup
    weightTree->SetBranchStatus("*", 0);
    weightTree->SetBranchStatus(runBranch.c_str(), 1);
    weightTree->SetBranchStatus(subrunBranch.c_str(), 1);
    weightTree->SetBranchStatus(eventBranch.c_str(), 1);

    // Variables to hold branch values
    int treeRun, treeSubrun, treeEvent;
    weightTree->SetBranchAddress(runBranch.c_str(), &treeRun);
    weightTree->SetBranchAddress(subrunBranch.c_str(), &treeSubrun);
    weightTree->SetBranchAddress(eventBranch.c_str(), &treeEvent);

    // Build RSE -> entry index map for weight tree
    std::cout << "  Building RSE index map for weight tree..." << std::endl;
    std::map<std::tuple<int,int,int>, Long64_t> rseToEntry;
    for (Long64_t i = 0; i < nWeightEntries; i++) {
        weightTree->GetEntry(i);
        rseToEntry[std::make_tuple(treeRun, treeSubrun, treeEvent)] = i;
        if (i % 100000 == 0) {
            std::cout << "    Indexed entry " << i << std::endl;
        }
    }
    std::cout << "  Index map built with " << rseToEntry.size() << " entries" << std::endl;

    // The weight map branch - need to handle as pointer
    // Now activating weightBranch, which is expensive.
    weightTree->SetBranchStatus(weightBranchName.c_str(), 1);    
    MapStringVecDouble* weightsPtr = nullptr;
    weightTree->SetBranchAddress(weightBranchName.c_str(), &weightsPtr);

    // ub_tune_weight: needed to make systematic variation reweighting is relative to nominal GENIE
    double ub_tune_weight = 0;    
    weightTree->SetBranchStatus("ub_tune_weight", 1 );
    weightTree->SetBranchAddress("ub_tune_weight", &ub_tune_weight);
    
    // Process all events
    int processedCount = 0;
    std::cout << "  Accumulating weights..." << std::endl;

    for (size_t iEvt = 0; iEvt < numEvents; iEvt++) {
        if (iEvt % 10000 == 0) {
            std::cout << "    Processing event " << iEvt << " / " << numEvents << std::endl;
        }

        // Get RSE for this event
        const auto& rse = rseList[iEvt];
        if (rse.size() < 3) continue;

        auto rseTuple = std::make_tuple(rse[0], rse[1], rse[2]);

        // Find entry in weight tree
        auto it = rseToEntry.find(rseTuple);
        if (it == rseToEntry.end()) {
            missingEventCount_++;
            continue;
        }

        // Load the weight entry
        size_t nbytes = weightTree->GetEntry(it->second);

        if (!weightsPtr || nbytes==0) {
            missingEventCount_++;
            continue;
        }

        const MapStringVecDouble& weights = *weightsPtr;
        double centralWeight = centralWeights[iEvt];
        const auto& binIndices = binIndicesList[iEvt];

        // Iterate over all parameters in the weight map
        for (const auto& paramPair : weights) {
            const std::string& parname = paramPair.first;
            const std::vector<double>& variations = paramPair.second;

            // Skip if not in our included list
            if (includedParams_.find(parname) == includedParams_.end()) {
                continue;
            }

            int nvariations = static_cast<int>(variations.size());
            if (nvariations > maxVariations_) {
                nvariations = maxVariations_;
            }

            // Track variations per parameter
            if (variationsPerParam_.find(parname) == variationsPerParam_.end()) {
                variationsPerParam_[parname] = nvariations;
            }

	    // For xsec parameters, we reweight the event back to genie nominal by removing the UB tune
	    double xsec_weight = 1.0;
	    if ( xsecParamNames_.find(parname) != xsecParamNames_.end() ) {
	      if ( ub_tune_weight>0.0 )
		xsec_weight = 1.0/ub_tune_weight;
	    }

            // Accumulate into each variable's bins
            for (int varIdx = 0; varIdx < numVariables_; varIdx++) {
                if (varIdx >= static_cast<int>(binIndices.size())) continue;

                int ibin = binIndices[varIdx];
                if (ibin < 0) continue;  // Variable doesn't apply to this event

                // Get or create array for this (var, param) combination
                auto key = std::make_pair(varIdx, parname);
                if (arrays_.find(key) == arrays_.end()) {
                    int nbins = binsPerVariable_[varIdx];
                    arrays_[key].assign(nbins * nvariations, 0.0);
                }
		if (badWeightsPerVariableBins_.find(key) == badWeightsPerVariableBins_.end()) {
		    int nbins = binsPerVariable_[varIdx];
		    badWeightsPerVariableBins_[key].assign(nbins, 0);
		}

                auto& arr = arrays_[key];
		auto& badweights = badWeightsPerVariableBins_[key];
                int nbins = binsPerVariable_[varIdx];

                // Fast inner loop - the core optimization
                for (int iUniv = 0; iUniv < nvariations; iUniv++) {
                    double w = variations[iUniv];
		    // Row-major: arr[ibin, iUniv] = arr[ibin * nvariations + iUniv]
		    int idx = ibin * nvariations + iUniv;		    
                    if (w < maxValidWeight_) {
                        if (idx < static_cast<int>(arr.size())) {
                            arr[idx] += w * centralWeight*xsec_weight;
                        }
                    } else {
		        // bad weight: either larger than max weight or NAN. set to 1.0.
		        std::cout << "badweight[" << varIdx << " | " << parname << "] weight=" << w << std::endl;
                        if (iUniv < static_cast<int>(badWeightsPerUniverse_.size())) {
                            badWeightsPerUniverse_[iUniv]++;
                        }
			badweights[ibin]++;
			arr[idx] += centralWeight*xsec_weight;
                    }
                }
            }
        }
        processedCount++;
    }

    weightFile->Close();
    delete weightFile;

    std::cout << "  Processed " << processedCount << " events, "
              << missingEventCount_ << " missing from weight tree" << std::endl;

    return processedCount;
}

const std::vector<double>& XsecFluxAccumulator::getArray(int varIndex,
                                                          const std::string& paramName) const
{
    auto key = std::make_pair(varIndex, paramName);
    auto it = arrays_.find(key);
    if (it == arrays_.end()) {
        static std::vector<double> empty;
        return empty;
    }
    return it->second;
}

std::vector<int>& XsecFluxAccumulator::getBadWeightsPerVarBin(int varIndex,std::string paramName)
{
    auto key = std::make_pair(varIndex, paramName);
    auto it = badWeightsPerVariableBins_.find(key);
    if (it == badWeightsPerVariableBins_.end()) {
        static std::vector<int> empty;
        return empty;
    }
    return it->second;  
}

const std::vector<int>& XsecFluxAccumulator::getBadWeightCounts() const
{
    return badWeightsPerUniverse_;
}

int XsecFluxAccumulator::getNumVariationsForParam(const std::string& paramName) const
{
    auto it = variationsPerParam_.find(paramName);
    if (it == variationsPerParam_.end()) return 0;
    return it->second;
}

int XsecFluxAccumulator::getNumBins(int varIndex) const
{
    if (varIndex < 0 || varIndex >= static_cast<int>(binsPerVariable_.size())) return 0;
    return binsPerVariable_[varIndex];
}

std::vector<std::string> XsecFluxAccumulator::getFoundParams() const
{
    std::vector<std::string> result;
    for (const auto& kv : variationsPerParam_) {
        result.push_back(kv.first);
    }
    return result;
}
