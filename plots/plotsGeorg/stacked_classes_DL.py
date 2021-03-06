###########
# imports #
###########

# Standard imports
import ROOT
import os
from array import array
from copy import deepcopy
import math

# RootTools
from RootTools.core.standard import *

# User specific 
from TopEFT.Tools.user import plot_directory
plot_directory_=os.path.join(plot_directory, 'DeepLepton')
plot_directory=plot_directory_

# plot samples definitions
from def_plot_samples import *

#parser
def get_parser():
    ''' Argument parser for post-processing module.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser for cmgPostProcessing")

    argParser.add_argument('--version',         action='store', type=str, choices=['v1'],                   required = True, help="Version for output directory")
    argParser.add_argument('--year',            action='store', type=int, choices=[2016,2017],              required = True, help="Which year?")
    argParser.add_argument('--flavour',         action='store', type=str, choices=['ele','muo'],            required = True, help="Which Flavour?")
    argParser.add_argument('--trainingDate',    action='store', type=int, default=0,                                         help="Which Training Date? 0 for no Training Date.")
    argParser.add_argument('--isTestData',      action='store', type=int, choices=[0,1],                    required = True, help="Which Training Date? 0 for no Training Date.")
    argParser.add_argument('--ptSelection',     action='store', type=str, choices=['pt_10_to_inf', 'pt_15_to_inf'],         required = True, help="Which pt selection?")
    argParser.add_argument('--sampleSelection', action='store', type=str, choices=['SlDlTTJetsVsQCD', 'DYVsQCD', 'DYVsQCD_ptRelSorted'],      required = True, help="Which sample selection?")
    argParser.add_argument('--trainingType',    action='store', type=str, choices=['std','iso'],            required = True, help="Standard or Isolation Training?")
    argParser.add_argument('--sampleSize',      action='store', type=str, choices=['small','medium','large','full'],         required = True, help="small sample or full sample?")

    #argParser.add_argument('--nJobs',        action='store', type=int,    nargs='?',         default=1,                   help="Maximum number of simultaneous jobs.")
    #argParser.add_argument('--job',          action='store', type=int,                       default=0,                   help="Run only job i")

    return argParser

options = get_parser().parse_args()

# adapted from RootTools (added fillstyle)
def fillStyle( color, style, lineColor = ROOT.kBlack, errors = False):
    def func( histo ):
        lc = lineColor if lineColor is not None else color
        histo.SetLineColor( lc )
        histo.SetMarkerSize( 0 )
        histo.SetMarkerStyle( 0 )
        histo.SetMarkerColor( lc )
        histo.SetFillColor( color )
        histo.SetFillStyle( style)
        histo.drawOption = "hist"
        if errors: histo.drawOption+='E'
        return 
    return func


##############################
# load samples and variables #
##############################

#define samples for electorns and muons
samples=plot_samples_v2(options.version, options.year, options.flavour, options.trainingDate, options.isTestData, options.ptSelection, options.sampleSelection, options.sampleSize)
    
# variables to read
read_variables=histo_plot_variables(options.trainingDate)

#########################
# define plot structure #
#########################

plotDate=samples["trainingDate"]

leptonFlavours=[]
ecalTypes=[]

if samples["leptonFlavour"]=="ele":
    sampleEle=samples["sample"]
    leptonFlavours.append({"Name":"Electron", "ShortName":"ele", "pdgId":11, "sample":sampleEle, "selectionString": "abs(lep_pdgId)==11", "date":plotDate})
    ecalTypes.append({"Name":"All", "selectionString": "abs(lep_etaSc)>=0."})
    ecalTypes.append({"Name":"EndCap", "selectionString": "abs(lep_etaSc)>1.479"})
    ecalTypes.append({"Name":"Barrel", "selectionString": "abs(lep_etaSc)<=1.479"})

if samples["leptonFlavour"]=="muo":
    sampleMuo=samples["sample"]
    leptonFlavours.append({"Name":"Muon", "ShortName":"muo", "pdgId":13, "sample":sampleMuo, "selectionString": "abs(lep_pdgId)==13", "date":plotDate})
    ecalTypes.append({"Name":"All", "selectionString": "abs(lep_eta)>=0."})

pt_cuts=[]
pt_cuts.append({"Name":"pt25toInf","lower_limit":25, "selectionString": "lep_pt>=25."})
if options.ptSelection=='pt_10_to_inf':
    pt_cuts.append({"Name":"pt10to25","lower_limit":10, "upper_limit":25, "selectionString": "lep_pt>=10.&&lep_pt<25."})
else:
    pt_cuts.append({"Name":"pt15to25","lower_limit":15, "upper_limit":25, "selectionString": "lep_pt>=15.&&lep_pt<25."})
    

isTestData=samples["isTestData"]  #1=true, 0=false

####################################
# loop over samples and draw plots #
####################################

for leptonFlavour in leptonFlavours:

    #define class samples
    samplePrompt    = deepcopy(leptonFlavour["sample"])
    sampleNonPrompt = deepcopy(leptonFlavour["sample"])
    sampleFake      = deepcopy(leptonFlavour["sample"])

    samplePrompt.setSelectionString("(lep_isPromptId==1&&"+leptonFlavour["selectionString"]+")")
    sampleNonPrompt.setSelectionString("(lep_isNonPromptId==1&&"+leptonFlavour["selectionString"]+")")
    sampleFake.setSelectionString("(lep_isFakeId==1&&"+leptonFlavour["selectionString"]+")")

    samplePrompt.name    = "Prompt"
    sampleNonPrompt.name = "NonPrompt"
    sampleFake.name      = "Fake"

    samplePrompt.texName    = "Prompt"
    sampleNonPrompt.texName = "NonPrompt"
    sampleFake.texName      = "Fake"

    samplePrompt.style    = fillStyle(color=ROOT.kCyan, style=3004, lineColor=ROOT.kCyan)
    sampleNonPrompt.style = fillStyle(color=ROOT.kBlue, style=3004, lineColor=ROOT.kBlue)
    sampleFake.style      = fillStyle(color=ROOT.kGray, style=3004, lineColor=ROOT.kGray)

    # Define stack
    mc    = [samplePrompt,sampleNonPrompt,sampleFake]  # A full example would be e.g. mc = [ttbar, ttz, ttw, ...]
    stack = Stack(mc) # A full example would be e.g. stack = Stack( mc, [data], [signal1], [signal2] ) -> Samples in "mc" are stacked in the plot

    for pt_cut in pt_cuts:
        for ecalType in ecalTypes:
                
            # Set some defaults -> these need not be specified below for each plot
            weight = staticmethod(lambda event, sample: 1.)  # could be e.g. weight = lambda event, sample: event.weight
            selectionString = "("+pt_cut["selectionString"]+"&&"+ecalType["selectionString"]+")" # could be a complicated cut
            Plot.setDefaults(stack = stack, weight = weight, selectionString = selectionString, addOverFlowBin='upper')
            plotname=""
            # Sequence
            sequence = []

            # Add a new fancy variable
            def make_absEInvMinusPInv( event, sample ):
                event.absEInvMinusPInv = abs(event.lep_eInvMinusPInv)
            sequence.append( make_absEInvMinusPInv)

            #def print_mcmatchId( event, sample ):
            #    if isNonPrompt(event) and event.lep_mvaIdSpring16<0.3 and sample==sample:
            #        print event.lep_mcMatchId

            #def print_class( event, sample ):
            #    assert isPrompt(event) + isNonPrompt(event) + isFake(event)==1, "Should never happen!"

            #    print event.lep_isPromptId, event.lep_isNonPromptId, event.lep_isFakeId, event.lep_mcMatchId, event.lep_mcMatchAny, isPrompt(event), isNonPrompt(event), isFake(event), event.lep_pdgId
            #    #print "Fill", event.lep_isPromptId if ((isPrompt(event) and sample==samplePrompt) or (isNonPrompt(event) and sample==sampleNonPrompt) or (isFake(event) and sample==sampleFake)) else float('nan')
            #    #print "Fill2", (isPrompt(event) and sample==samplePrompt),(isNonPrompt(event) and sample==sampleNonPrompt),(isFake(event) and sample==sampleFake)
            ##sequence.append(print_class)

            # Start with an empty list
            plots = []
            # Add plots

            #Lepton Classes
            plots.append(Plot(name=plotname+'ClassPrompt',
                texX = 'isPrompt', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_isPromptId,
                binning=[2,0,1],
            ))
            plots.append(Plot(name=plotname+'ClassNonPrompt',
                texX = 'isNonPrompt', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_isNonPromptId,
                binning=[2,0,1],
            ))
            plots.append(Plot(name=plotname+'ClassFake',
                texX = 'isFake', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_isFakeId,
                binning=[2,0,1],
            ))
            
            if not plotDate==0:
                plots.append(Plot(name=plotname+'DL_prob_isPrompt',
                    texX = 'DL_prob_isPrompt', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.prob_lep_isPromptId,
                    binning=[33,0,1],
                ))
                plots.append(Plot(name=plotname+'DL_prob_isNonPrompt',
                    texX = 'DL_prob_isNonPrompt', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.prob_lep_isNonPromptId,
                    binning=[33,0,1],
                ))
                plots.append(Plot(name=plotname+'DL_prob_isFake',
                    texX = 'DL_prob_isFake', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.prob_lep_isFakeId,
                    binning=[33,0,1],
                ))

            #Training Variables
            plots.append(Plot(name=plotname+'Pt',
                texX = 'pt', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_pt,
                binning=[100,0,500],
            ))
            plots.append(Plot(name=plotname+'Eta',
                texX = 'eta', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_eta,
                binning=[60,-3.2,3.2],
            ))
            plots.append(Plot(name=plotname+'Phi',
                texX = 'phi', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_phi,
                binning=[60,-3.2,3.2],
            ))
            plots.append(Plot(name=plotname+'Rho',
                texX = 'rho', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_rho,
                binning=[80,0,40],
            ))
            plots.append(Plot(name=plotname+'innerTrackChi2',
                texX = 'innerTrackChi2', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_innerTrackChi2,
                binning=[50,0,5] if leptonFlavour["Name"]=="Muon" else [50,0,10],
            ))
            plots.append(Plot(name=plotname+'RelIso03',
                texX = 'relIso03', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_relIso03,
                binning=[90,0,0.5],
            ))
            plots.append(Plot(name=plotname+'RelIso04',
                texX = 'relIso04', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_relIso04,
                binning=[90,0,0.7],
            ))
            plots.append(Plot(name=plotname+'miniRelIso',
                texX = 'miniRelIso', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_miniRelIso,
                binning=[90,0,0.5],
            ))
            plots.append(Plot(name=plotname+'LostOuterHits',
                texX = 'lostOuterHits', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_lostOuterHits,
                binning=[16,0,15],
            ))
            plots.append(Plot(name=plotname+'LostInnerHits',
                texX = 'lostInnerHits', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_lostHits,
                binning=[16,0,15],
            ))

            plots.append(Plot(name=plotname+'trackerLayers',
                texX = 'trackerLayers', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_trackerLayers,
                binning=[16,0,15],
            ))
            plots.append(Plot(name=plotname+'pixelLayers',
                texX = 'pixelLayers', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_pixelLayers,
                binning=[16,0,15],
            ))
            plots.append(Plot(name=plotname+'trackerHits',
                texX = 'trackerHits', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_trackerHits,
                binning=[16,0,15],
            ))
            plots.append(Plot(name=plotname+'innerTrackValidHitFraction',
                texX = 'innerTrackValidHitFraction', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_innerTrackValidHitFraction,
                binning=[50,0.9,1.0],
            ))
            plots.append(Plot(name=plotname+'jetDR',
                texX = 'jetDR', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_jetDR,
                binning=[50,0,0.1],
            ))
            plots.append(Plot(name=plotname+'Dxy',
                texX = 'dxy', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_dxy,
                binning=[60,-0.03,0.03] if leptonFlavour["Name"]=="Muon" else [60,-0.15,0.15],
            ))
            plots.append(Plot(name=plotname+'Dz',
                texX = 'dz', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_dz,
                binning=[60,-0.1,0.1] if leptonFlavour["Name"]=="Muon" else [60,-0.25,0.25],
            ))
            plots.append(Plot(name=plotname+'errorDxy',
                texX = 'errorDxy', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_edxy,
                binning=[50,0,0.004] if leptonFlavour["Name"]=="Muon" else [100,0,0.008],
            ))
            plots.append(Plot(name=plotname+'errorDz',
                texX = 'errorDz', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_edz,
                binning=[50,0,0.01] if leptonFlavour["Name"]=="Muon" else [100,0,0.02],
            ))
            plots.append(Plot(name=plotname+'d3DwrtPV',
                texX = 'd3DwrtPV', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_ip3d,
                binning=[100,0,0.02] if leptonFlavour["Name"]=="Muon" else [100,0,0.04],
            ))
            plots.append(Plot(name=plotname+'significanceD3DwrtPV',
                texX = 'significanceD3DwrtPV', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_sip3d,
                binning=[100,0,8],
            ))
            plots.append(Plot(name=plotname+'EffectiveArea03',
                texX = 'EffectiveArea03', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_EffectiveArea03,
                binning=[100,0,0.1] if leptonFlavour["Name"]=="Muon" else [300,0,0.3],
            ))
            plots.append(Plot(name=plotname+'jetPtRatiov1',
                texX = 'pt(lepton)/pt(nearestJet)', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_jetPtRatiov1,
                binning=[50,0,1],
            ))
            plots.append(Plot(name=plotname+'jetPtRatiov2',
                texX = 'pt(lepton)/[rawpt(jet-PU-lep)*L2L3Res+pt(lepton)]', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_jetPtRatiov2,
                binning=[50,0,1.25],
            ))
            plots.append(Plot(name=plotname+'jetPtRelv1',
                texX = 'lepPtTransverseToJetAxisV1', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_jetPtRelv1,
                binning=[100,0,7],
            ))
            plots.append(Plot(name=plotname+'jetPtRelv2',
                texX = 'lepPtTransverseToJetAxisV1', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_jetPtRelv2,
                binning=[200,0,20],
            ))
            plots.append(Plot(name=plotname+'ptErrTk',
                texX = 'ptErrorTrack', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_ptErrTk,
                binning=[100,0,10] if leptonFlavour["Name"]=="Muon" else [100,0,50],
            ))
            plots.append(Plot(name=plotname+'npfCand_neutral',
                texX = 'npfCand_neutral', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.npfCand_neutral,
                binning=[21,0,20],
            ))
            plots.append(Plot(name=plotname+'npfCand_charged',
                texX = 'npfCand_charged', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.npfCand_charged,
                binning=[71,0,70],
            ))
            plots.append(Plot(name=plotname+'npfCand_photon',
                texX = 'npfCand_photon', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.npfCand_photon,
                binning=[41,0,40],
            ))
            plots.append(Plot(name=plotname+'npfCand_electron',
                texX = 'npfCand_electron', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.npfCand_electron,
                binning=[21,0,20],
            ))
            plots.append(Plot(name=plotname+'npfCand_muon',
                texX = 'npfCand_muon', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.npfCand_muon,
                binning=[21,0,20],
            ))
            plots.append(Plot(name=plotname+'nTrueInt',
                texX = 'nTrueInt', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.nTrueInt,
                binning=[55,0,55],
            ))
            plots.append(Plot(name=plotname+'mvaTTH',
                texX = 'mvaTTH', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_mvaTTH, 
                binning=[30,-1,1],
            ))
            plots.append(Plot(name=plotname+'mvaTTV',
                texX = 'mvaTTV', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_mvaTTV, 
                binning=[30,-1,1],
            ))


            plots.append(Plot(name=plotname+'jetBTagCSV',
                texX = 'jetBTagCSV', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_jetBTagCSV, 
                binning=[30,0,1],
            ))
            plots.append(Plot(name=plotname+'jetBTagDeepCSV',
                texX = 'jetBTagDeepCSV', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_jetBTagDeepCSV, 
                binning=[30,0,1],
            ))
            plots.append(Plot(name=plotname+'jetBTagDeepCSVCvsB',
                texX = 'jetBTagDeepCSVCvsB', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_jetBTagDeepCSVCvsB, 
                binning=[30,0,1],
            ))
            plots.append(Plot(name=plotname+'jetBTagDeepCSVCvsL',
                texX = 'jetBTagDeepCSVCvsL', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_jetBTagDeepCSVCvsL, 
                binning=[30,0,1],
            ))
            #Electron specific
            if leptonFlavour["Name"]=="Electron":

                plots.append(Plot(name=plotname+'EtaSc',
                    texX = 'etaSc', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.lep_etaSc,
                    binning=[60,-3,3],
                ))
                plots.append(Plot(name=plotname+'SigmaIetaIeta',
                    texX = 'sigmaIetaIeta', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.lep_sigmaIEtaIEta,
                    binning=[30,0,0.06],
                ))
                plots.append(Plot(name=plotname+'Full5x5SigmaIetaIeta',
                    texX = 'full5x5_sigmaIetaIeta', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.lep_full5x5_sigmaIetaIeta,
                    binning=[30,0,0.06],
                ))
                plots.append(Plot(name=plotname+'DEtaInSeed',
                    texX = 'dEtaInSeed', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.lep_dEtaInSeed,
                    binning=[20,-0.04,0.04],
                ))
                plots.append(Plot(name=plotname+'DPhiScTrkIn',
                    texX = 'dPhiScTrkIn', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.lep_dPhiScTrkIn,
                    binning=[30,-0.3,0.3],
                ))
                plots.append(Plot(name=plotname+'DEtaScTrkIn',
                    texX = 'dEtaScTrkIn', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.lep_dEtaScTrkIn,
                    binning=[50,-5,5],
                ))
                plots.append(Plot(name=plotname+'EInvMinusPInv',
                    texX = '|1/E-1/p|', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.absEInvMinusPInv,
                    binning=[30,0,0.20],
                ))
                plots.append(Plot(name=plotname+'ConvVeto',
                    texX = 'convVeto', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.lep_convVeto,
                    binning=[2,0,1],
                ))
                plots.append(Plot(name=plotname+'HadronicOverEm',
                    texX = 'hadronicOverEm', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.lep_hadronicOverEm,
                    binning=[30,0,0.15],
                ))
                plots.append(Plot(name=plotname+'r9',
                    texX = 'r9', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.lep_r9,
                    binning=[100,0,1],
                ))
            #Muon specific
            if leptonFlavour["Name"]=="Muon":
                
                plots.append(Plot(name=plotname+'segmentCompatibility',
                    texX = 'segmentCompatibility', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.lep_segmentCompatibility,
                    binning=[10,0,1],
                ))
                plots.append(Plot(name=plotname+'muonInnerTrkRelErr',
                    texX = 'muonInnerTrkRelErr', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.lep_muonInnerTrkRelErr,
                    binning=[50,0,0.05],
                ))
                plots.append(Plot(name=plotname+'isGlobalMuon',
                    texX = 'isGlobalMuon', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.lep_isGlobalMuon,
                    binning=[2,0,1],
                ))
                plots.append(Plot(name=plotname+'chi2LocalPosition',
                    texX = 'chi2LocalPosition', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.lep_chi2LocalPosition,
                    binning=[100,0,10],
                ))
                plots.append(Plot(name=plotname+'chi2LocalMomentum',
                    texX = 'chi2LocalMomentum', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.lep_chi2LocalMomentum,
                    binning=[100,0,30],
                ))
                plots.append(Plot(name=plotname+'gobalTrackChi2',
                    texX = 'gobalTrackChi2', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.lep_globalTrackChi2,
                    binning=[50,0,3],
                ))
                plots.append(Plot(name=plotname+'gobalTrackProb',
                    texX = 'gobalTrackProb', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.lep_glbTrackProbability,
                    binning=[50,0,8],
                ))
                plots.append(Plot(name=plotname+'caloCompatibility',
                    texX = 'caloCompatibility', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.lep_caloCompatibility,
                    binning=[50,0,1],
                ))
                plots.append(Plot(name=plotname+'trkKink',
                    texX = 'trkKink', texY = 'Number of Events',
                    attribute = lambda lepton, sample: lepton.lep_trkKink,
                    binning=[100,0,50],
                ))
            #other Variables
            plots.append(Plot(name=plotname+'mcMatchId',
                texX = 'mcMatchId', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_mcMatchId,
                binning=[61,-30,30],
            ))
            plots.append(Plot(name=plotname+'mcMatchAny',
                texX = 'mcMatchAny', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_mcMatchAny,
                binning=[61,-30,30],
            ))
            plots.append(Plot(name=plotname+'pdgId',
                texX = 'pdgId', texY = 'Number of Events',
                attribute = lambda lepton, sample: lepton.lep_pdgId,
                binning=[61,-30,30],
            ))
            

            #plots.append(Plot( name = "fancy_variable",
            #    texX = 'Number of tracker hits squared', texY = 'Number of Events',
            #    attribute = lambda event, sample: event.fancy_variable, # <--- can use any 'event' attribute, including the ones we define in 'sequence'    binning=[30,0,900],
            #))


            # Fill everything.
            plotting.fill(plots, read_variables = read_variables, sequence = sequence)

            #
            # Helper: Add text on the plots
            #
            def drawObjects( plotData, dataMCScale, lumi_scale ):
                tex = ROOT.TLatex()
                tex.SetNDC()
                tex.SetTextSize(0.04)
                tex.SetTextAlign(11) # align right
                lines = [
                  (0.25, 0.95, 'TestData' if isTestData else 'TrainData'),
                  (0.55, 0.95, pt_cut["Name"]+" "+ecalType["Name"]+" "+leptonFlavour["Name"]+"s")
                ]
                return [tex.DrawLatex(*l) for l in lines]

            # Draw a plot and make it look nice-ish
            def drawPlots(plots, dataMCScale):
              for log in [False, True]:
                plot_directory_ = (os.path.join(
                                                plot_directory,
                                                str(options.year),
                                                options.flavour,
                                                options.sampleSelection,
                                                str(options.trainingDate) if not options.trainingDate==0 else options.sampleSize+'_sample',                
                                                'TestData' if isTestData else 'TrainData',
                                                'histograms', pt_cut["Name"]+"_"+ecalType["Name"], ("log" if log else "lin")
                                                ))
                for plot in plots:
                  #if not max(l[0].GetMaximum() for l in plot.histos): continue # Empty plot
                  
                  plotting.draw(plot,
                    plot_directory = plot_directory_,
                    #ratio = {'yRange':(0.1,1.9)} if not args.noData else None,
                    logX = False, logY = log, sorting = True,
                    yRange = (0.03, "auto") if log else (0.001, "auto"),
                    scaling = {},
                    legend = [ (0.15,0.9-0.03*sum(map(len, plot.histos)),0.9,0.9), 2],
                    drawObjects = drawObjects( False, dataMCScale , lumi_scale = -1 ),
                    copyIndexPHP = True
                  )


            # Draw the plots
            drawPlots(plots, dataMCScale = -1)

