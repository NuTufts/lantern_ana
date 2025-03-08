import sys, argparse
import numpy as np
import ROOT as rt
from math import sqrt
import yaml
rt.PyConfig.IgnoreCommandLineOptions = True
rt.gROOT.SetBatch(True)

#from helpers.larflowreco_ana_funcs import getCosThetaGravVector
#from selection_1g1p import run_1g1p_reco_selection_cuts
#from truthdef import truthdef_1gamma_cuts

from lantern_photon.SampleDataset import SampleDataset

parser = argparse.ArgumentParser("Make energy histograms from a bnb nu overlay ntuple file")
parser.add_argument("-c", "--config", type=str, required=True, help="input ntuple file")

args = parser.parse_args()

with open(args.config,'r')  as f:
  config = yaml.load(f)
  #print(config)

# Setup inputs
data_config = config['Inputs']
sampleDatasets = {}
for dataset,dataset_config in data_config['datasets'].items():
  input_dir_list = []
  sample_name = dataset_config['name']
  if 'input_dir_list' in data_config:
    input_dir_list = data_config['input_dir_list']
  sampleDatasets[sample_name] = SampleDataset.load_from_config( dataset_config, input_dir_list=input_dir_list )
  print("Opened dataset[",sample_name,"]: nentries=",len(sampleDatasets[sample_name]))

#we will scale histograms to expected event counts from POT in runs 1-3: 6.67e+20
targetPOT = 4.4e+19
targetPOTstring = "4.4e+19"
ntuplePOTsum = 0

failures = []

#For the new cosmic file
#cosmicPOTsum = 5.28e+19
#cosmicWeight = 0.4
cosmicPOTsum = 1.1e20
cosmicWeight = 1.0

# ROOT FILE TO SAVE Histograms
outrootfile = rt.TFile("outhist_separateEvaluator.root","recreate")
cosmic_event_list = open("cosmic_event_list.txt",'w')

#Variables for program function
fiducialData = {"xMin":0, "xMax":256,
                "yMin":-116.5, "yMax":116.5,
                "zMin":0, "zMax":1036,
                "width":15, "photonWidth":3.0,
                "vMin":np.array([0,-116.5,0.0]),
                "vMax":np.array([256.0,116.5,1036.0])}

classificationThreshold = 0
showerRecoThreshold = 10.0
showerFromTrack_sizethreshold=0
photonEDepThreshold = 5.0

# selection
from lantern_photon.selections.singlephoton_1gXp import run_1g1p_reco_selection_cuts
from lantern_photon.selections.singlephoton_truth import truthdef_1gamma_cuts

# Event Loop
eventTree = sampleDatasets['run3_bnbnu'].ntuple
for i in range(eventTree.GetEntries()):

  if False:
    break
  
  if i>0 and i%10000==0:
    print("eventTree Entry[",i,"]")
  
  eventTree.GetEntry(i)

  eventPassAllCuts, cuts_passed, recoList, recoTrackList, recoProtonCount = \
    run_1g1p_reco_selection_cuts( eventTree, classificationThreshold, showerRecoThreshold, showerFromTrack_sizethreshold, fiducialData, return_on_fail=False )
  recoPhotonInfo = cuts_passed.pop('recoPhotonInfo')

  passesTruthSelection, truth_cut_results, prim_photon_info = \
    truthdef_1gamma_cuts( eventTree, photonEDepThreshold, fiducialData, return_on_fail=False )

  if eventPassAllCuts==False:
    #print("entry[",i,"] passes original cuts, but does not pass selection function")
    #for cutname in cuts_passed:
    #  print("  [",cutname,"] ",cuts_passed[cutname])
    if passesTruthSelection:
      # lost a signal event. record information so we can study it visually
      recovtx = (0.0,0.0,0.0)
      if eventTree.foundVertex:
        recovtx = (eventTree.vtxX,eventTree.vtxY,eventTree.vtxZ)
      info_signal_lost = {
        "run":eventTree.run,
        "subrun":eventTree.subrun,
        "event":eventTree.event,
        "fileid":eventTree.fileid,
        "truevtx":(eventTree.trueVtxX,eventTree.trueVtxY,eventTree.trueVtxZ),
        "recovtx":recovtx,
        "nshowers":eventTree.nShowers,
        "ntracks":eventTree.nTracks
      }

      # save particular type of events
      # want to focus on wrong number of photons

      failures.append( info_signal_lost )

      print("RECO CUT RESULTS")
      print(cuts_passed)
      print("Num reco photons: ",len(recoPhotonInfo))
      for photoninfo in recoPhotonInfo:
        print('  ',photoninfo['index'],': ',photoninfo)
      print("TRUTH CUT RESULTS")
      print(truth_cut_results)
      print('true vertex: ',eventTree.trueVtxX,' ',eventTree.trueVtxY,' ',eventTree.trueVtxZ)
      for x in range(eventTree.nTrueSimParts):
        if eventTree.trueSimPartPDG[x] == 22:
          pixelList = [eventTree.trueSimPartPixelSumUplane[x]*0.0126,
                       eventTree.trueSimPartPixelSumVplane[x]*0.0126,
                       eventTree.trueSimPartPixelSumYplane[x]*0.0126]
          print(f"true photon: edep=( {pixelList[0]:.2f}, {pixelList[1]:.2f}, {pixelList[2]:.2f})")

      
      if len(failures)>=1:
        break
    continue

  if True:
    continue

sys.exit(0)
#   #PURITY - GRAPHING BASED ON TRUTH
  
#   #Calculating graphing values
#   leadingPhoton = scaleRecoEnergy(eventTree, recoList, recoTrackList)
#   #leadingPhoton = eventTree.vtxMaxIntimePixelSum*0.0126 # hack
#   #for recoIDX in recoList+recoTrackList:
#   #  leadingPhoton = eventTree.showerComp[recoIDX]

#   vertexDistX = eventTree.vtxX - eventTree.trueVtxX
#   vertexDistY = eventTree.vtxY - eventTree.trueVtxY
#   vertexDistZ = eventTree.vtxZ - eventTree.trueVtxZ
#   vertexDist = np.sqrt(vertexDistX**2 + vertexDistY**2 + vertexDistZ**2)
#   #if vertexDist < 3:
#   #  continue

#   #Now we make a list of the actual photons!
#   truePhotonIDs = truePhotonList(eventTree, fiducialData, threshold=photonEDepThreshold)
#   nEdepPhotons = len(truePhotonIDs)

#   missingPhotonDist2vtx = -1.0
#   missingPhotonEDep = -1.0
#   missingPhotonE = -1.0
#   for truePhotonIDX in truePhotonIDs:
#     truePhotonTID = eventTree.trueSimPartTID[truePhotonIDX]
#     idfound = False
#     for recoIDX in recoList:
#       if eventTree.showerTrueTID[recoIDX]==truePhotonTID:
#         idfound = True
#     for recoIDX in recoTrackList:
#       if eventTree.trackTrueTID[recoIDX]==truePhotonTID:
#         idfound = True
#     if not idfound:
#       # we missed this true photon
#       dist2vtx = 0.0
#       d2vx=eventTree.trueSimPartEDepX[truePhotonIDX]-eventTree.trueVtxX
#       d2vy=eventTree.trueSimPartEDepY[truePhotonIDX]-eventTree.trueVtxY
#       d2vz=eventTree.trueSimPartEDepZ[truePhotonIDX]-eventTree.trueVtxZ
#       dist2vtx = np.sqrt( d2vx*d2vx + d2vy*d2vy + d2vz*d2vz )
#       if missingPhotonDist2vtx<0.0 or dist2vtx < missingPhotonDist2vtx:
#         missingPhotonDist2vtx = dist2vtx

#       photonedep = eventTree.trueSimPartPixelSumYplane[truePhotonIDX]*0.0126
#       if missingPhotonEDep<0.0 or photonedep<missingPhotonEDep:
#         missingPhotonEDep = photonedep
      
#   #leadingPhoton = missingPhotonEDep

#   trueOpeningAngle = 0.0
#   if nEdepPhotons==2:    
#     id1 = truePhotonIDs[0]
#     id2 = truePhotonIDs[1]
#     trueOpeningAngle = trueTwoPhotonOpeningAngle( eventTree, truePhotonIDs[0], truePhotonIDs[1] )
#     if trueOpeningAngle<20.0:
#       nEdepPhotons=1
#   #leadingPhoton = trueOpeningAngle

#   # out of fiducial vertex
#   if trueCutFiducials(eventTree, fiducialData) == False:
#     if nEdepPhotons==1:
#       addHist(eventTree, recoProtonCount, fiducialPHists, leadingPhoton, eventTree.xsecWeight)
#     else:
#       addHist(eventTree, recoProtonCount, fiducialPHists2g, leadingPhoton, eventTree.xsecWeight)
#     continue
#   fiducialCount += 1
  
#   #Cut muons and electrons
#   if trueCutMuons(eventTree) == False:
#     addHist(eventTree, recoProtonCount, muonPHists, leadingPhoton, eventTree.xsecWeight)
#     continue
#   if trueCutElectrons(eventTree) == False:
#     addHist(eventTree, recoProtonCount, electronPHists, leadingPhoton, eventTree.xsecWeight)
#     continue
#   NCCount += 1

#   #pions and protons!
#   pionCount, protonCount = trueCutPionProton(eventTree)
#   if pionCount > 0:
#     addHist(eventTree, recoProtonCount, pionPHists, leadingPhoton, eventTree.xsecWeight)
#     continue
#   if protonCount > 1:
#     addHist(eventTree, recoProtonCount, protonPHists, leadingPhoton, eventTree.xsecWeight)
#     continue

#   noPionCount += 1


#   #Are there actually any photons?
#   if nEdepPhotons==0:
#     addHist(eventTree, recoProtonCount, noPhotonPHists, leadingPhoton, eventTree.xsecWeight)
#     continue
  
#   recoCount += 1
#   #Is there one Photon?
#   if nEdepPhotons==1:
#     if protonCount == 0:
#       addHist(eventTree, recoProtonCount, signalPHistsNoProton, leadingPhoton, eventTree.xsecWeight)
#     elif protonCount == 1:
#       addHist(eventTree, recoProtonCount, signalPHistsProton, leadingPhoton, eventTree.xsecWeight)
#     onePhoton += 1
#     continue
#   #Are there two?
#   elif nEdepPhotons == 2:
#     addHist(eventTree, recoProtonCount, twoPhotonPHists, leadingPhoton, eventTree.xsecWeight)
#     twoPhotons += 1
#     continue
  
#   #In that case, there should be at least three
#   else:
#     addHist(eventTree, recoProtonCount, manyPhotonPHists, leadingPhoton, eventTree.xsecWeight)
#     threePhotons += 1
#     continue

# with open('bnbnu_signal_cut.txt','w') as fout:
#   for info in failures:
#     vtx_x = info['recovtx'][0]
#     vtx_y = info['recovtx'][1]
#     vtx_z = info['recovtx'][2]
#     ntracks = info['ntracks']
#     nshowers = info['nshowers']
#     print(f'{info["run"]} {info["subrun"]} {info["event"]} {info["fileid"]} {vtx_x:.2f} {vtx_y:.2f} {vtx_z:.2f} {ntracks} {nshowers}',file=fout)
# sys.exit(0)

# #BEGINNING EVENT LOOP FOR COSMICS
# for i in range(cosmicTree.GetEntries()):
#   if i>0 and i%10000==0:
#     print("cosmicTree Entry[",i,"]")
#   cosmicTree.GetEntry(i)

#   cosmicEventPassAllCuts, cosmic_cuts_passed, recoList, recoTrackList, recoProtonCount = run_1g1p_reco_selection_cuts( cosmicTree,
#                                                                                                                        classificationThreshold,
#                                                                                                                        fiducialData )
#   untrackedCosmics += 1

#   if not cosmicEventPassAllCuts:
#     continue

#   #graphing based on photon count
#   #Calculating graphing values
#   leadingPhoton = scaleRecoEnergy(cosmicTree, recoList, recoTrackList)
#   #leadingPhoton = cosmicTree.vtxMaxIntimePixelSum*0.0126 # hack
#   #for recoIDX in recoList+recoTrackList:
#   #  leadingPhoton = cosmicTree.showerComp[recoIDX]  
#   addHist(cosmicTree, recoProtonCount, cosmicList, leadingPhoton, 1.0)

#   print(cosmicTree.run," ",cosmicTree.subrun," ",cosmicTree.event," ",cosmicTree.fileid, file=cosmic_event_list)


# #BEGINNING EVENT LOOP FOR COSMICS
# for i in range(nBeamEntries):
#   if i>0 and i%10000==0:
#     print("beamTree Entry[",i,"]")
#   beamTree.GetEntry(i)

#   beamPass, beam_cutspassed, recoList, recoTrackList, recoProtonCount = run_1g1p_reco_selection_cuts( beamTree, classificationThreshold, fiducialData )
#   if not beamPass:
#     continue

#   #graphing based on photon count
#   #Calculating graphing values
#   leadingPhoton = scaleRecoEnergy(beamTree, recoList, recoTrackList)
#   #leadingPhoton = beamTree.vtxMaxIntimePixelSum*0.0126 # hack
#   #for recoIDX in recoList+recoTrackList:
#   #  leadingPhoton = beamTree.showerComp[recoIDX]  
#   addHist(beamTree, recoProtonCount, beamList, leadingPhoton, 1.0)
  
# #BEGINNING EVENT LOOP FOR EFFICIENCY
# for i in range(eventTree.GetEntries()):

#   if i>0 and i%10000==0:
#     print("eventTree Entry[",i,"]")
  
#   eventTree.GetEntry(i)

#   # #Selecting events using truth
#   # if trueCutFiducials(eventTree, fiducialData) == False:
#   #   continue
  
#   # if trueCutMuons(eventTree) == False:
#   #   continue

#   # if trueCutElectrons(eventTree) == False:
#   #   continue

#   # #if trueCutCosmic(eventTree) == False:
#   # #  continue

#   # pionCount, protonCount = trueCutPionProton(eventTree)
#   # if pionCount > 0:
#   #   continue
#   # if protonCount > 1:
#   #   continue

#   # truePhotonIDs = truePhotonList(eventTree, fiducialData, threshold=photonEDepThreshold)
#   # nEdepPhotons = len(truePhotonIDs)
#   # trueOpeningAngle = 0.0
#   # if nEdepPhotons==2:
#   #   # WC inclusive opening angle acceptance
#   #   id1 = truePhotonIDs[0]
#   #   id2 = truePhotonIDs[1]
#   #   trueOpeningAngle = trueTwoPhotonOpeningAngle( eventTree, truePhotonIDs[0], truePhotonIDs[1] )
#   #   if trueOpeningAngle<20.0:
#   #     nEdepPhotons=1

#   # if nEdepPhotons != 1:
#   #   continue
#   passes_truthdef, truthcuts = truthdef_1gamma_cuts( eventTree, photonEDepThreshold, fiducialData, return_on_fail=True )
#   if not passes_truthdef:
#     continue

#   nEdepPhotons = truthcuts["NEdepPhotons"]
#   trueOpeningAngle = truthcuts["trueOpeningAngle"]
#   truePhotonIDs = truthcuts["truePhotonIDs"]
#   protonCount = truthcuts["protonCount"]
  
#   #EFFICIENCY - GRAPHING BASED ON RECO

#   leadingPhoton = scaleTrueEnergy(eventTree, truePhotonIDs)
#   passTruth += 1

#   if recoNoVertex(eventTree) == False:
#     addHist(eventTree, protonCount, effNoVertexHists, leadingPhoton, eventTree.xsecWeight)
#     continue
#   hasVertex += 1
#   #See if the event is neutral current                                                                                                  
#   #if recoNeutralCurrent(eventTree) == False:
#   #  addHist(eventTree, truePhotonIDs, emptyList, effCCHists, leadingPhoton, eventTree.xsecWeight)
#   #  continue

#   #Check for above-threshold muons and electrons 
#   if recoCutMuons(eventTree, classificationThreshold) == False:
#     addHist(eventTree, protonCount, effMuonHists, leadingPhoton, eventTree.xsecWeight)
#     continue

#   if recoCutElectrons(eventTree, classificationThreshold) == False:
#     addHist(eventTree, protonCount, effElectronHists, leadingPhoton, eventTree.xsecWeight)
#     continue

#   hasNC += 1

#   #Use Matt's Cosmic Cut
#   if trueCutCosmic(eventTree) == False:
#     addHist(eventTree, protonCount, effCosmicPixelHists, leadingPhoton, eventTree.xsecWeight)
  
#   #Cut events with vertexes outside the fiducial
#   if recoFiducials(eventTree, fiducialData) == False:
#     addHist(eventTree, protonCount, effFiducialHists, leadingPhoton, eventTree.xsecWeight)
#     continue
#   inFiducial += 1

#   #Cut events with pions present
#   if recoPion(eventTree, classificationThreshold) == False:
#     addHist(eventTree, protonCount, effPionHists, leadingPhoton, eventTree.xsecWeight)
#     continue
#   pionProtonFine += 1
  
#   #Cut events with too many protons
#   recoProtonCount = recoProton(eventTree, classificationThreshold)
#   if recoProtonCount > 1:
#     addHist(eventTree, protonCount, effProtonHists, leadingPhoton, eventTree.xsecWeight)
#     continue


#   #See if there are any photons in the event - if so, list them
#   recoList = recoPhotonListFiducial(fiducialData, eventTree, showerRecoThreshold)
#   recoTrackList = recoPhotonListTracks(fiducialData, eventTree, classificationThreshold)
#   #recoTrackList = []

#   # only 1 photon reco cut happens here
#   if len(recoList) + len(recoTrackList) != 1:
#     if len(recoList) + len(recoTrackList) == 0:
#       addHist(eventTree, protonCount, effNoPhotonHists, leadingPhoton, eventTree.xsecWeight)
#       noEffPhotons += 1    
#       continue
#     elif len(recoList) + len(recoTrackList) == 2:
#       addHist(eventTree, protonCount, effTwoPhotonHists, leadingPhoton, eventTree.xsecWeight)
#       twoEffPhotons += 1
#       continue
#     else:
#       addHist(eventTree, protonCount, effManyPhotonHists, leadingPhoton, eventTree.xsecWeight)
#       manyEffPhotons += 1
#       continue
    
#   #Try cutting for Shower from Charged Score 
#   if recoCutShowerFromChargeScore(eventTree, recoList, recoTrackList) == False:
#     addHist(eventTree, protonCount, effShowerChargeHists, leadingPhoton, eventTree.xsecWeight)
#     continue

#   #Cut based on Primary Score
#   if recoCutPrimary(eventTree, recoList, recoTrackList) == False:
#     addHist(eventTree, protonCount, effPrimaryHists, leadingPhoton, eventTree.xsecWeight)
#     continue

#   #Try cutting based on data for Track Lengths
#   if recoCutLongTracks(eventTree, fiducialData) == False:
#     addHist(eventTree, protonCount, effLongTrackHists, leadingPhoton, eventTree.xsecWeight)
#     continue

#   #Cut based on the completeness of known Muons
#   if recoCutMuonCompleteness(eventTree) == False:
#     addHist(eventTree, protonCount, effMuonCompHists, leadingPhoton, eventTree.xsecWeight)
#     continue

#   # meant to reduce vertices selected when there is a clear in-time muon
#   if recoCutMaxInTime(eventTree, protonCount) == False:
#     addHist(eventTree, protonCount, effMaxInTimeHists, leadingPhoton, eventTree.xsecWeight)
#     continue

#   if recoCutCompleteness(eventTree, recoList, recoTrackList)==False:    
#     addHist(eventTree, protonCount, effShowerCompHists, leadingPhoton, eventTree.xsecWeight)
#     continue

#   survivesCuts += 1

#   #Now we're pretty sure the event is legitimate, so we go ahead and graph based on the number of photons
#   addHist(eventTree, protonCount, effOnePhotonHists, leadingPhoton, eventTree.xsecWeight)
#   oneEffPhoton += 1

# #LOOPS OVER - HISTOGRAM ORGANIZING TIME

# #Scaling the Cosmic Histograms
# for hist in cosmicList:
#   hist.Scale((targetPOT/cosmicPOTsum)*(ntuplePOTsum/targetPOT)) # the second factor is there to get canceled in histstacktwosignal


# #Stacking histograms
# # Prediction with purity categories
# purityCanvas1, purityStack1, purityLegend1, purityInt1 = histStackTwoSignal("1 Gamma + 0 Sample", pList1,
#                                                                             ntuplePOTsum, targetPOT, beamOnePhoton)
# purityProtonCanvas1, purityProtonStack1, purityProtonLegend1, purityProtonInt1 = histStackTwoSignal("1 Gamma + 1P Sample", pProtonList1,
#                                                                                                     ntuplePOTsum, targetPOT, protonBeamOnePhoton)

# # efficiency
# effCanvas1, effStack1, effLegend1, effInt1 = histStack("TrueOutcomes1", "True 1 Gamma + 0  Outcomes", effList1, ntuplePOTsum)
# effProtonCanvas1, effProtonStack1, effProtonLegend1, effProtonInt1 = histStack("TrueOutcomes1P", "True 1 Gamma + 1P  Outcomes", effProtonList1, ntuplePOTsum)

# writeList = [purityCanvas1, purityProtonCanvas1, effCanvas1, effProtonCanvas1]

# for stack in [purityStack1, purityProtonStack1]:
#   stack.GetXaxis().SetTitle("Reconstructed Leading Photon Energy (GeV)")
#   print(stack.GetName(),": ",stack.GetMaximum())

# for stack in [effStack1, effProtonStack1]:
#   stack.GetXaxis().SetTitle("True LeadingPhoton Energy (GeV)")

# for stack in [effStack1, effProtonStack1, purityStack1, purityProtonStack1]:
#   stack.GetYaxis().SetTitle("Events per 4.4e19 POT")

# #Now all that's left to do is write the canvases to the file
# outFile = rt.TFile(args.outfile, "RECREATE")
# for n,canvas in enumerate(writeList):
#   canvas.cd()
#   if n==0:
#     beamOnePhoton.Draw("E1same")
#   elif n==1:
#     protonBeamOnePhoton.Draw("E1same")
#   else:
#     pass
#   canvas.Update()
#   canvas.Write()

# outrootfile.Write()
  
# print("PURITY STATS:")
# print("Neutral Current:", NCCount)
# print("In Fiducial:", fiducialCount)
# print("No pions, protons:", noPionCount)
# print("Fully reconstructed:", recoCount)
# print(onePhoton, "events had one photon")
# print(twoPhotons, "events had two photons")
# print(threePhotons, "events had 3+ photons")

# print("EFFICIENCY STATS:")
# print("Total signal space:", passTruth)
# print("Total with vertex:", hasVertex)
# print("Total NC:", hasNC)
# print("Total reconstructed in Fiducial:", inFiducial)
# print("Total with acceptable pion/protons:", pionProtonFine)
# print("Total that survive our cuts:", survivesCuts)
# print("Total with no photons:", noEffPhotons)
# print("Total with one photon:", oneEffPhoton)
# print("Total with two photons:", twoEffPhotons)
# print("Total with three photons:", manyEffPhotons)

# print("POTsum:", ntuplePOTsum)

# print("There were", totalCosmics, "total cosmics")
# print(vertexCosmics, "had a reconstructed vertex")
# print(noVertexCosmics, "had no reconstructed vertex")


# #print("Average vertex distance:", sum(distList)/len(distList))
