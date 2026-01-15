#ifndef __LANTERN_ANA_XSECFLUX_ACCUMULATOR__
#define __LANTERN_ANA_XSECFLUX_ACCUMULATOR__

#include <vector>
#include <string>
#include <map>
#include <set>
#include "TFile.h"
#include "TTree.h"
#include "TChain.h"
#include "MapTypes.h"

/**
 * @class XsecFluxAccumulator
 * @brief Accumulates event weights across universe variations for systematic uncertainty estimation.
 *
 * This class provides fast C++ implementation for accumulating weights from
 * cross-section and flux systematic variations into histogram bins.
 * It processes all passing events in a single call, reading weights directly
 * from the weight TTree.
 */
class XsecFluxAccumulator {

public:
    XsecFluxAccumulator();
    ~XsecFluxAccumulator();

    /**
     * @brief Configure the accumulator with bin and parameter information.
     * @param numVariables Number of observable variables being histogrammed
     * @param binsPerVariable Number of bins (including under/overflow) for each variable
     * @param paramNames List of systematic parameter names to include
     * @param maxVariations Maximum number of universe variations to process
     * @param maxValidWeight Cap on valid weights (larger weights are flagged as bad)
     */
    void configure(int numVariables,
                   const std::vector<int>& binsPerVariable,
                   const std::vector<std::string>& paramNames,
                   int maxVariations,
                   double maxValidWeight);

    /**
     * @brief Reset all accumulators to zero (call before processing a new sample).
     */
    void reset();

    /**
     * @brief Process all passing events and accumulate weights.
     *
     * This is the main workhorse function. It:
     * 1. Opens the weight tree file
     * 2. Builds an RSE -> entry index map
     * 3. Loops over all passing events
     * 4. For each event, reads weights and accumulates into appropriate bins
     *
     * @param weightFilePath Path to the ROOT file containing the weight tree
     * @param weightTreeName Name of the TTree containing systematic weights
     * @param weightBranchName Name of the branch containing the weight map
     * @param runBranch Name of run branch in weight tree
     * @param subrunBranch Name of subrun branch in weight tree
     * @param eventBranch Name of event branch in weight tree
     * @param rseList Vector of (run, subrun, event) tuples for passing events
     * @param binIndicesList Vector of bin indices for each variable, for each event
     * @param centralWeights Vector of central value weights for each event
     * @return Number of events successfully processed
     */
    int processAllEvents(const std::string& weightFilePath,
                         const std::string& weightTreeName,
                         const std::string& weightBranchName,
                         const std::string& runBranch,
                         const std::string& subrunBranch,
                         const std::string& eventBranch,
                         const std::vector<std::vector<int>>& rseList,
                         const std::vector<std::vector<int>>& binIndicesList,
                         const std::vector<double>& centralWeights);

    /**
     * @brief Get the accumulated weight array for a specific (variable, parameter) combination.
     * @param varIndex Index of the variable (0-based)
     * @param paramName Name of the systematic parameter
     * @return Reference to the accumulated array (nbins x nvariations, flattened row-major)
     */
    const std::vector<double>& getArray(int varIndex, const std::string& paramName) const;

    /**
     * @brief Get the number of bad weights encountered per universe.
     * @return Reference to vector of bad weight counts
     */
    const std::vector<int>& getBadWeightCounts() const;

    /**
     * @brief Get the number of variations found for a specific parameter.
     * @param paramName Name of the systematic parameter
     * @return Number of variations, or 0 if parameter not found
     */
    int getNumVariationsForParam(const std::string& paramName) const;

    /**
     * @brief Get number of bins for a variable.
     * @param varIndex Index of the variable
     * @return Number of bins including under/overflow
     */
    int getNumBins(int varIndex) const;

    /**
     * @brief Get list of parameter names that were actually found in the weight tree.
     * @return Vector of parameter names
     */
    std::vector<std::string> getFoundParams() const;

    /**
     * @brief Get number of missing events (RSE not found in weight tree).
     * @return Count of missing events
     */
    int getMissingEventCount() const { return missingEventCount_; }

private:
    // Configuration
    int numVariables_;
    std::vector<int> binsPerVariable_;
    std::set<std::string> includedParams_;
    int maxVariations_;
    double maxValidWeight_;
    bool configured_;

    // Storage: key is (varIndex, paramName), value is flattened array [bin * nvariations + universe]
    std::map<std::pair<int, std::string>, std::vector<double>> arrays_;

    // Track actual number of variations per parameter (may differ between params)
    std::map<std::string, int> variationsPerParam_;

    // Bad weight tracking
    std::vector<int> badWeightsPerUniverse_;

    // Missing event tracking
    int missingEventCount_;

    // Helper to find tree in file (may be in TDirectoryFile)
    TTree* findTreeInFile(TFile* file, const std::string& treeName);
};

#endif
