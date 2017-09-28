#run in CMSSW_8_0_21
from WMCore.Configuration import Configuration
config = Configuration()

config.section_("General")
config.General.requestName = "tmp"
config.General.workArea = 'crab_ewkDM_mAOD'
config.General.transferLogs = True

config.section_("JobType")
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = '../cfg/RECOmAOD.py'
config.JobType.disableAutomaticOutputCollection = False

config.section_("Data")
config.Data.splitting = 'FileBased'
#config.Data.splitting = 'Automatic'

config.Data.unitsPerJob = 5
#config.Data.totalUnits  = 50000 
config.Data.publication = True
config.Data.inputDBS = 'phys03'
config.Data.publishDBS = 'phys03'

config.Data.outputDatasetTag = 'ewkDM_mAOD'
#config.Data.outLFNDirBase = '/store/user/%s/' % (getUsernameFromSiteDB())

config.section_("Site")
config.Site.storageSite = 'T2_AT_Vienna'
#config.Site.whitelist = ['T2_*']

config.section_("User")


if __name__ == '__main__':
    from CRABAPI.RawCommand import crabCommand
    for input_dataset in [
  '/ewkDM_ttZ_ll_DC2A_0p200000_DC2V_0p200000/schoef-ewkDM-19898e58c9c00509372f15bcc801ecbe/USER',
  '/ewkDM_ttZ_ll_DC1A_0p600000_DC1V_m0p240000_DC2V_m0p250000/schoef-ewkDM-19898e58c9c00509372f15bcc801ecbe/USER',
  '/ewkDM_ttZ_ll_DC1A_0p600000_DC1V_m0p240000_DC2V_0p250000/schoef-ewkDM-19898e58c9c00509372f15bcc801ecbe/USER',
  '/ewkDM_ttZ_ll_DC1A_0p600000_DC1V_m0p240000_DC2A_m0p250000/schoef-ewkDM-19898e58c9c00509372f15bcc801ecbe/USER',
  '/ewkDM_ttZ_ll_DC1A_0p600000_DC1V_m0p240000_DC2A_m0p176700_DC2V_m0p176700/schoef-ewkDM-19898e58c9c00509372f15bcc801ecbe/USER',
  '/ewkDM_ttZ_ll_DC1A_0p600000_DC1V_m0p240000_DC2A_m0p176700_DC2V_0p176700/schoef-ewkDM-19898e58c9c00509372f15bcc801ecbe/USER',
  '/ewkDM_ttZ_ll_DC1A_0p600000_DC1V_m0p240000_DC2A_0p250000/schoef-ewkDM-19898e58c9c00509372f15bcc801ecbe/USER',
  '/ewkDM_ttZ_ll_DC1A_0p600000_DC1V_m0p240000_DC2A_0p176700_DC2V_m0p176700/schoef-ewkDM-19898e58c9c00509372f15bcc801ecbe/USER',
  '/ewkDM_ttZ_ll_DC1A_0p600000_DC1V_m0p240000_DC2A_0p176700_DC2V_0p176700/schoef-ewkDM-19898e58c9c00509372f15bcc801ecbe/USER',
  '/ewkDM_ttZ_ll_DC1A_0p500000_DC1V_m1p000000/schoef-ewkDM-19898e58c9c00509372f15bcc801ecbe/USER',
  '/ewkDM_ttZ_ll_DC1A_0p500000_DC1V_0p500000/schoef-ewkDM-19898e58c9c00509372f15bcc801ecbe/USER',
  '/ewkDM_ttZ_ll/schoef-ewkDM-19898e58c9c00509372f15bcc801ecbe/USER',
    ]:
        config.Data.inputDataset = input_dataset
        config.General.requestName = input_dataset.split('/')[1] 
        
        #crabCommand('submit', '--dryrun', config = config)
        crabCommand('submit', config = config)
