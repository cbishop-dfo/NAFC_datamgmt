import pandas as pd

# Creates a df of ships number, name long, and name short
# Creates and returns a pandas dataframe for ships
# This toolkit is used specifically for Biological data
# indexes  ------------------------
# [0] - ship number
# [1] - ship name long
# [2] - ship name short

# Changed for Biological
# need - ned
# spec - spc

def createShipDF():
    ships = [
        ['00', 'unknown', 'xxx'],
        ['01', 'a.t.cameron', 'xxx'],
        ['02', 'gadus', 'gadus'],
        ['03', 'shamook', 'sham'],
        ['04', 'marinus', 'mar'],
        ['05', 'kenda', 'ken'],
        ['06', 'martin&phillip', 'xxx'],
        ['07', 'zagreb', 'xxx'],
        ['08', 'burin_bay', 'xxx'],
        ['09', 'nfld_hawk', 'hawk'],
        ['10', 'tman', 'tem'],
        ['11', 'hammond', 'ham'],
        ['12', 'needler', 'ned'],
        ['13', 'cindy_elizabeth', 'xxx'],
        ['14', 'balder_cabot', 'xxx'],
        ['15', 'specials', 'spc'],
        ['16', 'e.e.prince', 'xxx'],
        ['17', 'lake_melville', 'xxx'],
        ['18', 'dawson', 'dawson'],
        ['19', 'karl&jackie', 'xxx'],
        ['20', 'hudson', 'hud'],
        ['21', 'parizeau', 'par'],
        ['22', 'petrel', 'petrel'],
        ['23', 'cormorant', 'corm'],
        ['24', 'bernier', 'bern'],
        ['25', 'hood', 'hood'],
        ['26', 'mares', 'mar'],
        ['27', 'ccg206', 'ccg'],
        ['27', 'ccg206', 'cg'], # Added duplicate to match biomass
        ['28', 'adair', 'adair'],
        ['29', 'lauzier', 'lauz'],
        ['30', 'nfld_lynx', 'lynx'],
        ['31', 'kingfisher', 'kfisher'],
        ['32', 'surf', 'surf'],
        ['33', 'roger', 'roger'],
        ['34', 'explorer', 'exp'],
        ['35', 'zandvoort', 'zand'],
        ['36', 'aharvey', 'har'],
        ['37', 'larsen', 'lar'],
        ['38', 'gilbert', 'gil'],
        ['39', 'teleost', 'tel'],
        ['40', 'whaler', 'whal'],
        ['41', 'sentinal', 'sent'],
        ['42', 'aclare', 'aclare'],
        ['44', 'lindsey', 'lind'],
        ['45', 'grenfell', 'gren'],
        ['48', 'cape_ballard', 'ballard'],
        ['49', 'pennysmart', 'ps'],
        ['50', 'naka', 'naka50'],
        ['51', 'naka', 'naka51'],
        ['52', 'naka', 'naka52'],
        ['53', 'naka', 'naka53'],
        ['54', 'gilbertbay', 'gbmpa'],
        ['55', 'discovery', 'discovery'],
        ['59', 'pearkes', 'pearkes'],
        ['60', 'celtic_explorer', 'cel'],
        ['61', 'vladykov', 'vlad'],
        ['62', 'aqviq', 'aqv'],
        ['63', 'kinguk', 'kinguk'],
        ['64', 'katsheshuk', 'katsheshuk'],
        ['65', 'martha_black', 'martha'],
        ['66', 'EcoSciences', 'ecosci'],
        ['70', 'aquaculture', 'aqua'],
        ['71', 'aquaculture2', 'aqua2'],
        ['72', 'aquaculture3', 'aqua3'],
        ['75', 'viking_s27', 'viks'],
        ['76', 'Cartier', 'cart'],
        ['77', 'Cabot', 'cabot'],
        ['79', 'james_cook', 'coo'],
        ['80', 'afap80', 'afap80'],
        ['81', 'afap81', 'afap81'],
        ['82', 'afap82', 'afap82'],
        ['83', 'afap83', 'afap83'],
        ['84', 'afap84', 'afap84'],
        ['85', 'afap85', 'afap85'],
        ['86', 'afap86', 'afap86'],
        ['89', 'afap89', 'afap89'],
        ['90', 'meds_data', 'meds90'],
        ['91', 'olabs', 'olabs'],
        ['92', 'french', 'doc'],
        ['93', 'osc', 'osc'],
        ['94', 'spanish', 'spanish'],
        ['95', 'meds_data', 'meds95'],
        ['96', 'meds_data', 'meds96'],
        ['AA', 'sent_AA', 'AA'],
        ['AB', 'sent_AB', 'AB'],
        ['AC', 'sent_AC', 'AC'],
        ['AD', 'sent_AD', 'AD'],
        ['AE', 'sent_AE', 'AE'],
        ['AF', 'sent_AF', 'AF'],
        ['AG', 'sent_AG', 'AG'],
        ['AH', 'sent_AH', 'AH'],
        ['AI', 'sent_AI', 'AI'],
        ['AJ', 'sent_AJ', 'AJ'],
        ['AK', 'sent_AK', 'AK'],
        ['AL', 'sent_AL', 'AL'],
        ['AM', 'sent_AM', 'AM'],
        ['AN', 'sent_AN', 'AN'],
        ['AO', 'sent_AO', 'AO'],
        ['AP', 'sent_AP', 'AP'],
        ['AQ', 'sent_AQ', 'AQ'],
        ['AR', 'sent_AR', 'AR'],
        ['AS', 'sent_AS', 'AS'],
        ['AT', 'sent_AT', 'AT'],
        ['AU', 'sent_AU', 'AU'],
        ['AV', 'sent_AV', 'AV'],
        ['AW', 'sent_AW', 'AW'],
        ['AX', 'sent_AX', 'AX'],
        ['AY', 'sent_AY', 'AY'],
        ['AZ', 'sent_AZ', 'AZ']]

    ship_df = pd.DataFrame.from_records(ships)
    return ship_df

###########################################################################################################

def getShipName(cast, shipDF=createShipDF()):
    try:
        s = shipDF[shipDF[0].str.match(cast.ship.__str__())]
        sname = s.values[0][2]
        cast.ShipName = sname
    except Exception as e:
        cast.ShipName = "xxx"
        print(e.__str__())
        print("Cannot Find Match Given Ship Number...")
        print("Ship Number: " + cast.ship.__str__())

###########################################################################################################

def getShipNumber(cast, shipDF=createShipDF()):

    try:
        s = shipDF[shipDF[2].str.match(cast.ShipName.__str__())]
        snumber = s.values[0][0]
        cast.ship = snumber
    except Exception as e:
        cast.ship = "00"
        print(e.__str__())
        print("Cannot Find Match Given Ship Name...")
        print("Ship Name: " + cast.ShipName.__str__())

###########################################################################################################



if __name__ == '__main__':
    df = createShipDF()
