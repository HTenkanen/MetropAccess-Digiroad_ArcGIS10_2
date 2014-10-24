# -*- coding: iso-8859-1 -*-
#------------------------------
# METROPACCESS-DIGIROAD
# MetropAccess-tutkimushanke
# HELSINGIN YLIOPISTO
# Koodi: Henrikki Tenkanen
#-------------------------------
# 5. Palvelualueen laskenta
#-------------------------------

####################################################################################
#MetropAccess-Digiroad, ty�kalu Digiroad-aineiston muokkaukseen MetropAccess-hankkeen menetelm�n mukaisesti
#    Copyright (C) 2014  MetropAccess (Tenkanen). For MetropAccess-project and contact details, please see http://blogs.helsinki.fi/accessibility/
# 
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###################################################################################

import arcpy, sys, time, string, os
from arcpy import env

#Pametrit:
Facilities = arcpy.GetParameterAsText(0)
IndKohteet = arcpy.GetParameterAsText(1)
NetworkData = arcpy.GetParameterAsText(2)
LiikenneElementti = arcpy.GetParameterAsText(3)
Nimi = arcpy.GetParameterAsText(4)
Impedanssi = arcpy.GetParameterAsText(5)
Breaks = arcpy.GetParameterAsText(6)
Pysakointi = arcpy.GetParameterAsText(7)
Kavely = int(arcpy.GetParameterAsText(8))
Suunta = arcpy.GetParameterAsText(9)
Details = arcpy.GetParameterAsText(10)
Overlap = arcpy.GetParameterAsText(11)
Trim = arcpy.GetParameterAsText(12)
TrimCut = arcpy.GetParameterAsText(13)

#Lis�Parametreja jotka ovat helposti k�ytt��n otettavissa (koodattu valmiiksi):

#RinDisk = arcpy.GetParameterAsText(14) #Otettavissa k�ytt��n koodia muokkaamalla
#Lines = arcpy.GetParameterAsText(15) #Voidaan lis�t� tarvittaessa parametriksi, t�ll�in t�m� pit�� lis�t� my�s k�ytt�liittym�n viimeiseksi kysytt�v�ksi parametriksi!


#Environment m��ritykset:
temp = os.path.dirname(NetworkData) #Kirjoitusoikeuksien varmistamiseksi k�ytet��n temp-kansiona input-tiedostojen kansiota ###arcpy.GetSystemEnvironment("TEMP") 
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd, "*")[0]

env.workspace = temp

#Tsekataan onko temp geodatabase vai tavallinen kansio:
if ".gdb" in temp or ".mdb" in temp:
    gdbCheck = True
    #Etsit��n geodatabasen 'juuri'
    try:
        pos = temp.index('.gdb')
    except:
        pos = temp.index('.mdb')
    temp = temp[:pos+4]
else:
    gdbCheck = False

#Tsekataan sis�lt��k� Nimi v�lily�ntej�
Nimi = Nimi.replace(" ", "_")
    
#Haetaan ArcGis versio:
for key, value in arcpy.GetInstallInfo().iteritems():
    if key == "Version":
        ArcVersio = value

#Luodaan suoritusinfopalkki
arcpy.SetProgressor("step", "PALVELUALUE LASKENTA...Tarkistukset ennen laskentaa...", 0, 100, 5) 

#Suoritusinfot:
def Aloitus():
    aika = time.asctime()
    teksti = "Aloitus: " + aika
    arcpy.AddMessage(teksti)

def Valmis():
    aika = time.asctime()
    teksti = "Valmis: " + aika
    arcpy.AddMessage(teksti)

def msg(Message):
    arcpy.AddMessage(Message)

def virhe(Virheilmoitus):
    arcpy.AddError(Virheilmoitus)
    sys.exit()

msg(temp)

#Metodit/m��ritykset:

arcpy.overwriteOutputs = True

def AddLayerToMap(addLayer):
 mxd = arcpy.mapping.MapDocument("CURRENT")
 df = arcpy.mapping.ListDataFrames(mxd, "*")[0]
 arcpy.mapping.AddLayer(df, addLayer, "TOP")
 arcpy.RefreshActiveView()
 arcpy.RefreshTOC()
 del mxd, df, addLayer

def AddLayerToGroup(addLayer, Group):
 mxd = arcpy.mapping.MapDocument("CURRENT")
 df = arcpy.mapping.ListDataFrames(mxd, "*")[0]
 targetGroupLayer = arcpy.mapping.ListLayers(mxd, Group, df)[0]
 arcpy.mapping.AddLayerToGroup(df, targetGroupLayer, addLayer, "TOP")
 arcpy.RefreshActiveView()
 arcpy.RefreshTOC()
 del mxd, df, addLayer

def SetName(Layer, Name):
 mxd = arcpy.mapping.MapDocument("CURRENT")
 df = arcpy.mapping.ListDataFrames(mxd, "*")[0]
 Kohde = arcpy.mapping.ListLayers(mxd, Layer, df)[0]
 Kohde.name = Name
 arcpy.RefreshActiveView()
 arcpy.RefreshTOC()
 del mxd, df, Kohde


def ExDel(haettava):
    if arcpy.Exists(haettava):
        arcpy.Delete_management(haettava)

msg("------------------------------")
msg("METROPACCESS-DIGIROAD")
msg("MetropAccess-tutkimushanke")
msg("HELSINGIN YLIOPISTO")
msg("-------------------------------")
msg("5. Palvelualueen laskenta")
msg("-------------------------------")

time.sleep(2.5)

#---------------------------------------------------
#TARKISTUKSET
#---------------------------------------------------

#Tarkistetaan Network Datasetin muuttujat
msg("Tarkistetaan Network Dataset")
Aloitus()

desc = arcpy.Describe(NetworkData)
attributes = desc.attributes
NDparams = []
for attribute in attributes:
    NDparams.append(attribute.name)

NDPath = desc.path

if gdbCheck == False:
    LiikenneElementit = NDPath + "\\" + desc.edgeSources[0].name + ".shp" #Parsitaan sourcedatan (Liikenne_Elementit) polku ja nimi
else:
    LiikenneElementit = NDPath + "\\" + desc.edgeSources[0].name #Parsitaan sourcedatan (Liikenne_Elementit) polku ja nimi

arcpy.SetProgressorPosition(5)

Haettava = ["Digiroa_aa", "Kokopva_aa", "Keskpva_aa", "Ruuhka_aa", "Pituus"]
Nro = 0
Accumulation = []
for x in range(5):
    if Haettava[Nro] in NDparams:
        Accumulation.append(Haettava[Nro])
        Nro += 1
    else:
        Nro += 1

#Tarkistetaan, ett� impedanssi on olemassa:
if len(Accumulation) == 0:
    VL = arcpy.ListFields(LiikenneElementit, Impedanssi)
    VC = len(VL)
    if VC == 1:
        Accumulation.append(Impedanssi)  #K�ytet��n k�ytt�j�n omaa impedanssikentt�� laskentaan ja Accumulaatio kentt�n�.
        msg("K�ytt�j�n m��rittelem� impedanssi!")
    else:
        virhe("VIRHE! M��ritelty� impedanssia ei l�ydy Liikenne_Elementti -taulusta. Tarkista, ett� muuttuja on todella olemassa \nja ett� Impedanssikent�n kirjoitusasu t�sm�� k�ytett�v�n muuttujan kanssa. ")
else:
    if Impedanssi in Accumulation:
        True
    else:
        VL = arcpy.ListFields(LiikenneElementit, Impedanssi)
        VC = len(VL)
        if VC == 1:
            Accumulation.append(Impedanssi)
            msg("K�ytt�j�n m��rittelem� impedanssi!")
        else:
            virhe("VIRHE! M��ritelty� impedanssia ei l�ydy Network Datasetist�. Tarkista, ett� muuttuja on todella olemassa \nja ett� Impedanssikent�n kirjoitusasu t�sm�� k�ytett�v�n muuttujan kanssa. ")


#Tarkistetaan ett� Group-layerit l�ytyv�t:
polku = os.path.dirname(os.path.realpath(__file__)) #M��ritet��n python skriptin polku
Lyrpolku = polku + "\\" + "lyr"

SAGroup = Lyrpolku + "\\" + "Service_Areas.lyr"
AikaGroup = Lyrpolku + "\\" + "Sort_by_Time.lyr"

if os.path.isdir(Lyrpolku) != True:
    teksti = "ERROR: Kansiota: " + Lyrpolku.encode('utf-8') + " ei l�ydy! Tarkista, ett� kansioon: " + polku.encode('utf-8') + ", on sijoitettu MetropAccess-Digiroad ty�kalun mukana tuleva lyr-kansio tiedostoineen."
    virhe(teksti)
    
if os.path.isfile(SAGroup) != True:
    teksti = "ERROR: Kansiosta: " + Lyrpolku.encode('utf-8') + " ei l�ydy tarvittavaa tiedostoa 'Service_Areas.lyr'! Tarkista, ett� MetropAccess-Digiroad ty�kalun mukana tullut tiedosto varmasti l�ytyy kansiosta."
    virhe(teksti)
    
if os.path.isfile(AikaGroup) != True:
    teksti = "ERROR: Kansiosta: " + Lyrpolku.encode('utf-8') + " ei l�ydy tarvittavaa tiedostoa 'Sort_by_Time.lyr'! Tarkista, ett� MetropAccess-Digiroad ty�kalun mukana tullut tiedosto varmasti l�ytyy kansiosta."
    virhe(teksti)
    
Valmis()
arcpy.SetProgressorPosition(10)
msg("----------------------------")

#-------------------------------------------------
#M��RITET��N PROJEKTIOT SAMAAN
#-------------------------------------------------

env.workspace = temp

arcpy.SetProgressorLabel("PALVELUALUE LASKENTA...Tarkistetaan koordinaattij�rjestelm�t...")
msg("Tarkistetaan koordinaattij�rjestelm�t")
Aloitus()

#Tarkistetaan ND-projektio:
Desc = arcpy.Describe(NetworkData)
NDProjektio = Desc.spatialReference.factoryCode

if NDProjektio in [3067,2391,2392,2393,2394,104129]:
    True
else:
    virhe("Tieverkkoaineiston tulee olla projisoituna joko EUREF_FIN_TM35FIN:iin, GCS_EUREF_FIN:iin tai Finland_Zone_1, 2, 3 tai -4:��n (KKJ). Muuta Liikenne_elementti.shp projektio johonkin n�ist� Project -ty�kalulla, luo uusi Network Dataset perustuen t�h�n uuteen projisoituun LiikenneElementti -tiedostoon ja aja ty�kalu uudelleen.")

del Desc

#Tarkistetaan laskettavien kohteiden prjektio:
Desc = arcpy.Describe(Facilities)
Projektio = Desc.spatialReference.Name
FactCode = Desc.spatialReference.factoryCode
Proj = Projektio[:8]

#M��ritet��n tiedostopolut
if gdbCheck == False:
    FacilitiesProj = "FacilitiesProj.shp"
    FPath = temp + "\\" + FacilitiesProj
    Kantis = "Kantakaupunki.shp"
    KantisPath = temp + "\\" + "KantisProj.shp"
else:
    FacilitiesProj= "FacilitiesProj"
    FPath = temp + "\\" + FacilitiesProj
    Kantis = "Kantakaupunki"
    KantisPath = temp + "\\" + "KantisProj"

#Luodaan spatial reference perustuen NetworkDatan SR:een:
sr = arcpy.SpatialReference()
if NDProjektio == 3067: #EurefFin
    sr.factoryCode = 3067
    sr.create()
elif NDProjektio == 104129: #GCS_EurefFIN
    sr.factoryCode = 104129
    sr.create()
elif NDProjektio == 2391: #KKJ1
    sr.factoryCode = 2391
    sr.create()
elif NDProjektio == 2392: #KKJ2
    sr.factoryCode = 2392
    sr.create()
elif NDProjektio == 2393: #KKJ3
    sr.factoryCode = 2393
    sr.create()
elif NDProjektio == 2394: #KKJ4
    sr.factoryCode = 2394
    sr.create()

#M��ritet��n Laskettaville kohteille sama projektio, jos NetworkData on EUREF_FIN_TM35FIN:iss� tai GCS_EUREF_FIN:iss�:
if NDProjektio == 3067 or NDProjektio == 104129:
    if NDProjektio != FactCode:
        if FactCode >= 2391 and FactCode <= 2394:
            transform_method = "KKJ_To_EUREF_FIN"
        elif FactCode == 3067:
            transform_method = ""
        elif Proj == "WGS_1984" or FactCode == 4326: #Projected WGS_1984 tai GCS_WGS_1984
            transform_method = "EUREF_FIN_To_WGS_1984"
        elif Proj == "ETRS_198":
            transform_method = "EUREF_FIN_To_ETRS_1989"
        else:
            virhe("Laskettavat kohteet tulee olla projisoituna johonkin seuraavista koordinaatistoista: KKJ, EUREF_FIN, WGS_1984, ETRS_1989")
                           
        ExDel(FPath)
        
        arcpy.Project_management(Facilities, FPath, sr, transform_method) #M��ritet��n Destinationit samaan koordinaatistoon
        Facilities = FPath
        msg("Laskettavien kohteiden projektio vaihdettiin samaksi kuin Network Datalla. Luotiin kopio tiedostosta.")

#M��ritet��n laskettaville kohteille sama projektio, jos NetworkData on KKJ:ssa:
elif NDProjektio == 2391 or NDProjektio == 2392 or NDProjektio == 2393 or NDProjektio == 2394:
    if NDProjektio != FactCode: #Jos NetworkData ja kohdepisteet ovat eri KKJ:ssa projisoidaan ne samaan.
        if FactCode >= 2391 and FactCode <= 2394:
            transform_method = ""
        elif Proj == "WGS_1984" or FactCode == 4326: #Projected WGS_1984 tai GCS_WGS_1984
            transform_method = "KKJ_To_WGS_1984_2_JHS153"
        elif Proj == "ETRS_198":
            transform_method = "KKJ_To_ETRS_1989_2"
        else:
            virhe("Kohdepisteet tulee olla projisoituna johonkin seuraavista koordinaatistoista:")
            virhe("KKJ, EUREF_FIN, WGS_1984, ETRS_1989")
        
        ExDel(FPath)
        
        arcpy.Project_management(Facilities, FPath, sr, transform_method) #M��ritet��n Destinationit samaan koordinaatistoon
        Facilities = FPath
        msg("Laskettavien kohteiden projektio vaihdettiin samaksi kuin Network Datalla. Luotiin kopio tiedostosta.")

arcpy.SetProgressor("step", "PALVELUALUE LASKENTA...Tarkistetaan koordinaattij�rjestelm�t...", 0, 100, 5)
arcpy.SetProgressorPosition(15)    
Valmis()
msg("----------------------------")

#-------------------------------------------------------------------------------------
#Luodaan kantakaupunki polygoni jos k�velyaika parkkipaikalle halutaan ottaa huomioon:
#-------------------------------------------------------------------------------------

if int(Kavely) > 0 or Pysakointi != "0":
  
    #M��ritet��n polygonien kulmien koordinaatit:
    coordList = [[387678.024778,6675360.99039],[387891.53396,6670403.35286],[383453.380944,6670212.21613],[383239.871737,6675169.85373],[387678.024778,6675360.99039]] #Koordinaatit ovat EUREF_FIN_TM35FIN:iss�
    point = arcpy.Point()
    array = arcpy.Array()

    #Lis�t��n koordinaatit Arrayhin:
    for coordPair in coordList:
        point.X = coordPair[0]
        point.Y = coordPair[1]
        array.add(point)

    Kantakaupunki = arcpy.Polygon(array)

    arcpy.SetProgressor("step", "PALVELUALUE LASKENTA...Tarkistetaan koordinaattij�rjestelm�t...", 0, 100, 5) #Infopalkki pit�� alustaa uudelleen (Arc-bugittaa)
    arcpy.SetProgressorPosition(20)  

    #M��ritet��n Spatial Reference:
    sr = arcpy.SpatialReference()
    sr.factoryCode = 3067
    sr.create()

    #Luodaan kantakaupunki tiedosto:
    msg("Luodaan kantakaupunkipolygoni")

    ExDel(Kantis)
    arcpy.Select_analysis(Kantakaupunki, Kantis)

    #M��ritet��n kantakaupungille projektio:
    arcpy.DefineProjection_management(Kantis, sr)

    #M��ritet��n kantakaupungin projektio samaan kuin Network Datan:
    ExDel(KantisPath)

    del sr
    sr = arcpy.SpatialReference()
    if NDProjektio == 3067: #EurefFin
        sr.factoryCode = 3067
        sr.create()
    elif NDProjektio == 104129: #GCS_EurefFIN
        sr.factoryCode = 104129
        sr.create()
    elif NDProjektio == 2391: #KKJ1
        sr.factoryCode = 2391
        sr.create()
    elif NDProjektio == 2392: #KKJ2
        sr.factoryCode = 2392
        sr.create()
    elif NDProjektio == 2393: #KKJ3
        sr.factoryCode = 2393
        sr.create()
    elif NDProjektio == 2394: #KKJ4
        sr.factoryCode = 2394
        sr.create()

    if NDProjektio == 104129:
        arcpy.Project_management(Kantis, KantisPath, sr, "") #M��ritet��n kantakaupunki samaan koordinaatistoon
        Kantakaupunki = KantisPath

    elif NDProjektio == 2391 or NDProjektio == 2392 or NDProjektio == 2393 or NDProjektio == 2394:
        arcpy.Project_management(Kantis, KantisPath, sr, "KKJ_To_EUREF_FIN") #M��ritet��n kantakaupunki samaan koordinaatistoon
        Kantakaupunki = KantisPath

#------------------------------------------
#PARAMETRIEN TARKISTUS
#------------------------------------------

msg("Tarkistetaan parametrit")
arcpy.SetProgressor("step", "PALVELUALUE LASKENTA...Tarkistetaan parametrit...", 0, 100, 5)
arcpy.SetProgressorPosition(20)
Aloitus()

#Tarkistetaan kohteiden erotus:
if IndKohteet == 'true':
    
    msg("Laskettavat kohteet halutaan erikseen")
    arcpy.SetProgressorLabel("PALVELUALUE LASKENTA...Luodaan kohde-layerit...")
    #Tehd��n jokaisesta kohteen rivist� oma Feature layerins�:
    FacilFeat = "FacilFeat"
    ExDel(FacilFeat)

    arcpy.MakeFeatureLayer_management(Facilities, FacilFeat, "", temp, "")   #Tehd��n Laskettavista kohteista oma feature layerins�

    rivit = int(arcpy.GetCount_management(FacilFeat).getOutput(0)) #Katsotaan montako kohdetta l�ytyy

    #Alustetaan nimet ja indeksi:
    #GeodataBasessa indeksi l�htee ykk�sest�!!!
    if gdbCheck == False:
        i = 0
    else:
        i = 1
        
    FNimi = temp + "\\" + "Kohde_" + str(i) + "_lyr" #Alustetaan kohteen nimi

    if gdbCheck == False:
        FaciPath = temp + "\\" + "Kohde_" + str(i) + ".shp" #Kohdetiedosto
    else:
        FaciPath = temp + "\\" + "Kohde_" + str(i) #Kohdetiedosto
        
    FaciList = [[],[]]               #Luodaan kohteille lista
    Step = (30.0 / rivit)
    Progress = 20
        
    msg("Luodaan kohde-layerit")
                
    for rivi in range(rivit):
            
        ExDel(FaciPath)

        if gdbCheck == False:
            FID = "FID = " + str(i)
        else:
            FID = "OBJECTID = " + str(i)

        arcpy.Select_analysis(FacilFeat, FaciPath, FID) #Valitaan jokainen tiedoston rivi yksi kerrallaan

        FaciList[0].append(os.path.basename(FaciPath)) #Lis�t��n kohteen nimi listaan
        
        #Jos halutaan ottaa k�vely parkkipaikalle huomioon merkit��n kohteelle tieto onko se kantakaupungissa vai sen ulkopuolella:
        if int(Kavely) > 0:
            ExDel(FNimi)
            arcpy.MakeFeatureLayer_management(Facilities, FNimi, FID, temp, "")
                                    
            #Katsotaan onko piste kantakaupungin sis�ll�:
            arcpy.SelectLayerByLocation_management(FNimi, "INTERSECT", Kantakaupunki, "", "NEW_SELECTION")

            #Katsotaan onko rivi valittuna vai ei:
            desc = arcpy.Describe(FNimi)
            Valinta = desc.FIDSet
            del desc
            
            if Valinta == "": #Jos piste ei ole kantakaupungin sis�ll� annetaan arvoksi 1
                FaciList[1].append(0)
            else: #Jos piste on kantakaupungin sis�ll� annetaan arvoksi 0
                FaciList[1].append(1)

        #P�ivitykset:
        i += 1
        
        if gdbCheck == False:
            FNimi = temp + "\\" + "Kohde_" + str(i) + "_lyr" #Alustetaan kohteen nimi
            FaciPath = temp + "\\" + "Kohde_" + str(i) + ".shp" #P�ivitet��n kohdetiedosto
            FID = "FID = " + str(i) #P�ivitet��n ehto
        else:
            FNimi = temp + "\\" + "Kohde_" + str(i) + "_lyr" #Alustetaan kohteen nimi
            FaciPath = temp + "\\" + "Kohde_" + str(i) #P�ivitet��n kohdetiedosto
            FID = "OBJECTID = " + str(i) #P�ivitet��n ehto
                
        Progress = int(Progress + Step)
        arcpy.SetProgressorPosition(Progress)

arcpy.SetProgressorPosition(50)

#--------------------------------
#Tarkistetaan Breaks arvot:

if Breaks.find(",") == -1: #Tarkistetaan onko pilkkuja
    True
else:
    Breaks = Breaks.replace(",", " ") #Korvataan pilkut whitespacella
if Breaks.find("  ") == -1: #Tarkistetaan onko liian pitki� v�lej�
    True
else:
    Breaks = Breaks.replace("  ", " ") #Korvataan liian pitk�t v�lit 1:ll� whitespacella
if Breaks.find("   ") == -1: #Tarkistetaan onko liian pitki� v�lej�
    True
else:
    Breaks = Breaks.replace("   ", " ") #Korvataan liian pitk�t v�lit 1:ll� whitespacella
#--------------------------------

#Tarkistetaan suunta:

if Suunta == "Pois laskettavista kohteista":
    Suunta = "TRAVEL_FROM" #The service area is created in the direction away from the facilities. 
elif Suunta == "Kohti laskettavia kohteita":
    Suunta = "TRAVEL_TO"   #The service area is created in the direction towards the facilities.
else:
    Suunta = "TRAVEL_FROM" #The service area is created in the direction away from the facilities. 

#--------------------------------

#Tarkistetaan Polygonin piirtotarkkuus:
if Details == "1":
    Details = "SIMPLE_POLYS"
elif "Hierarkia" not in NDparams and Details == "2":
    Details = "DETAILED_POLYS"
elif "Hierarkia" in NDparams and Details == "2" and ArcVersio != "10.1": #Jos hierarkiaa k�ytet��n ei voida k�ytt�� Detailed Polygoneja ArcGIS 10.1!
    Details = "DETAILED_POLYS"
elif Details == "3":
    Details = "NO_POLYS"
else:
    Details = "SIMPLE_POLYS"

#--------------------------------    

###Tarkistetaan kuinka polygonit halutaan piirt��:
##PolyInd = 0 #Triggerin oletus
##if RinDisk == "1": #Tehd��n erilliset Layerit jokaisesta polygonista (hitaampi laskenta - analyysien kannalta j�rkev�mpi)
##    PolyInd = 1      #M��ritet��n triggeri, ett� aletaan suorittamaan erillisten Service Areoiden laskentaa
##    RinDisk = "DISKS" #Tekee ainoastaan yhden Service Area layerin - Service area ei sis�ll� l�hemp�n� l�ht�pistett� sijaitsevia vy�hykkeit� (rinkulat)
##elif RinDisk == "2":
##    RinDisk = "DISKS" #Tekee ainoastaan yhden Service Area layerin - Service area ei sis�ll� l�hemp�n� l�ht�pistett� sijaitsevia vy�hykkeit� (rinkulat)
##elif RinDisk == "3":
##    RinDisk = "RINGS" #Jokainen Service Area vy�hyke sis�lt�� my�s l�hemp�n� l�ht�pistett� sijaitsevat vy�hykkeet
##else:
##    RinDisk = "DISKS"

RinDisk = "DISKS"

#--------------------------------
#Tarkistetaan Overlap:
    
if Overlap == "1":
    Overlap = "NO_MERGE" #Kaikille kohteille tehd��n omat polygonit, jotka voivat menn� my�s p��llekk�in.
elif Overlap == "2":
    Overlap = "NO_OVERLAP" #Kaikille kohteille tehd��n omat polygonit, jotka eiv�t voi menn� p��llekk�in (Dominanssialue). 
elif Overlap == "3":
    Overlap = "MERGE" #Yhdist�� saman Break arvon omaavat polygonit yhteen.
else:
    Overlap = "NO_MERGE"

#--------------------------------
#Tarkistetaan polygonin Trimmaus:

if "Hierarkia" in NDparams and ArcVersio == "10.1": #Jos hierarkiaa k�ytet��n ei voida k�ytt�� Trimmi�
    Trim = "NO_TRIM_POLYS"
elif Trim == "False":
    Trim = "NO_TRIM_POLYS"
elif Trim == "True":
    Trim = "TRIM_POLYS"

#--------------------------------
#Tarkistetaan Trimmaus cutoff:

if Trim == "TRIM_POLYS":
    if int(TrimCut) > 0:
        TrimCut = TrimCut
    else:
        TrimCut = "100"
else:
    TrimCut = "100"

#--------------------------------
#Lines piirto (voi lis�t� tarvittaessa parametriksi - huom pit�� lis�t� t�ll�in my�s k�ytt�liittym��n parametriksi):

#if Lines == "0":
#    Lines = "NO_LINES"
#elif Lines == "1":
#    Lines = "TRUE_LINES"
#elif Lines == "2":
#    Lines = "TRUE_LINES_WITH_MEASURES"
#else:
Lines = "NO_LINES"

Valmis()
arcpy.SetProgressorPosition(55)
msg("----------------------------")


#-------------------------------------------------
#LUODAAN SERVICE AREAT
#-------------------------------------------------    

msg("Luodaan palvelualueet")
arcpy.SetProgressorLabel("PALVELUALUE LASKENTA...Luodaan palvelualueet...")
Aloitus()

#Erotetaan Breaks valuet listan alkioiksi:
BreakNimi = string.split(Breaks, " ")
BreakList = string.split(Breaks, " ")
BreakCount = len(BreakList)
Step = int(25.0 / BreakCount)
Progress = 55

#Lis�t��n Service Area group Layer kartalle:
SAGroup = Lyrpolku + "\\" + "Service_Areas.lyr"
AddLyr = arcpy.mapping.Layer(SAGroup)
AddLayerToMap(AddLyr)

#Lis�t��n Service Area grouppiin Group by Time:
AikaGroup = Lyrpolku + "\\" + "Sort_by_Time.lyr"
AddLyr = arcpy.mapping.Layer(AikaGroup)
AddLayerToGroup(AddLyr, "Service Areas")

if IndKohteet == 'true': #Katsotaan halutaanko aika-arvo-polygonit erilleen
    msg("Erotetaan aika-arvot omiksi layereikseen")
    
    #--------------------------------------------------------------------------------------
    #AIKA-ARVOT ERIKSEEN (POLYGONIT)
    #--------------------------------------------------------------------------------------
    infoCheck = False 
    for Break in BreakList:

        
        #Haetaan indeksi:
        i = BreakList.index(Break)
        
        for facility in FaciList[0]:

            #Haetaan indeksi:
            f = FaciList[0].index(facility)

            #Luodaan layer nimi:
            BreakName = BreakNimi[i] + "min_" + Nimi + "_" + facility

            try:
                arcpy.Delete_management(BreakName)
            except:
                pass

            Kohde = facility
            Kohde = Kohde.replace("Kohde_", "Facility_")

            #---------------------------------------------------------------------------------------------
            #PYS�K�INNIN HUOMIOON OTTAMINEN:
            #---------------------------------------------------------------------------------------------
            if Pysakointi != "0":
                                    
                #-------------------------------------------------------------------------------------
                #M��ritet��n Breaks-arvot uudelleen perustuen pys�k�intityyppiin (ja k�velynopeuteen):
                #-------------------------------------------------------------------------------------
           
                if Kavely > 0: #Katsotaan halutaanko k�vely� parkkipaikalle ottaa huomioon
                                    
                    KavelySisa = 180.0 / Kavely
                    KavelyUlko = 135.0 / Kavely
                                            
                    #Muutetaan Breaks arvoja ainoastaan, jos niit� ei ole viel� muutettu:
                    if Break == BreakNimi[i]:
                    
                        if FaciList[1][f] == 1: #Katsotaan onko piste kantakaupungin sis�ll�
                            #M��ritet��n uudet Breaks-arvot
                            if Pysakointi == "1":
                                Break = str(int(float(Break) - 0.42 - KavelySisa))
                            elif Pysakointi == "2":
                                Break = str(int(float(Break) - 0.73 - KavelySisa))
                            elif Pysakointi == "3":
                                Break = str(int(float(Break) - 0.22 - KavelySisa))
                            elif Pysakointi == "4":
                                Break = str(int(float(Break) - 0.16 - KavelySisa))

                        elif FaciList[1][f] == 0: #Katsotaan onko piste kantakaupungin ulkopuolella
                            #M��ritet��n uudet Breaks-arvot
                            if Pysakointi == "1":
                                Break = str(int(float(Break) - 0.42 - KavelyUlko))
                            elif Pysakointi == "2":
                                Break = str(int(float(Break) - 0.73 - KavelyUlko))
                            elif Pysakointi == "3":
                                Break = str(int(float(Break) - 0.22 - KavelyUlko))
                            elif Pysakointi == "4":
                                Break = str(int(float(Break) - 0.16 - KavelyUlko))

                else: #Jos k�vely� parkkipaikalle ei haluta ottaa huomioon

                    #Muutetaan Breaks arvoja ainoastaan, jos niit� ei ole viel� muutettu:
                    if Break == BreakNimi[i]:
                        if Pysakointi == "1":
                            Break = str(int(float(Break) - 0.42))
                        elif Pysakointi == "2":
                            Break = str(int(float(Break) - 0.73))
                        elif Pysakointi == "3":
                            Break = str(int(float(Break) - 0.22))
                        elif Pysakointi == "4":
                            Break = str(int(float(Break) - 0.16))
                #----------------------------------------------------------------------------------------

                            
            #Tehd��n ServiceAreaLayer:
            if float(Break) <= 0.0:
                if infoCheck == False:
                    teksti = "Break arvo: " + Break + ". Palvelualueen raja-arvoksi muodoistui <= 0 minuuttia! Ei laskettu palvelualuetta."
                    msg(teksti)
                    infoCheck = True
            else:
                
                arcpy.MakeServiceAreaLayer_na(NetworkData, BreakName, Impedanssi, Suunta, Break, Details, Overlap, RinDisk, Lines, "OVERLAP", "NO_SPLIT", "", Accumulation, "ALLOW_DEAD_ENDS_ONLY", "", Trim, TrimCut, "")
                            
                #Lis�t��n yksitellen kohteet Facilityiksi:
                facility = temp + "\\" + facility
                    
                arcpy.AddLocations_na(BreakName, "Facilities", facility, "", "1000 Meters", "", "", "MATCH_TO_CLOSEST", "CLEAR", "NO_SNAP", "5 Meters", "EXCLUDE", "")
                              
                #Suoritetaan laskenta:
                arcpy.Solve_na(BreakName)

                #Lis�t��n kartalle:
                Poly = BreakName + "/" + "Polygons"
                Timesort = BreakNimi[i] + "min_" + Nimi + "_" + Kohde
                FacRename = arcpy.mapping.Layer(Poly).name = Timesort #Muutetaan nimi

                AddLyr = arcpy.mapping.Layer(FacRename)
                Group = "Sort_by_Time"
                AddLayerToGroup(AddLyr, Group)
                           

        Progress = int(Progress + Step)
        arcpy.SetProgressorPosition(Progress)
        
        
#----------------------------------------------------------------------------------------
#Jos polygoneja eik� kohteita haluta erottaa suoritetaan normaali Service Area laskenta:
#----------------------------------------------------------------------------------------            
else:
    #Luodaan Service Area Layer:
    arcpy.MakeServiceAreaLayer_na(NetworkData, Nimi, Impedanssi, Suunta, Breaks, Details, Overlap, RinDisk, Lines, "OVERLAP", "NO_SPLIT", "", Accumulation, "ALLOW_DEAD_ENDS_ONLY", "", Trim, TrimCut, "")
    arcpy.SetProgressorPosition(60)
    
    #Lis�t��n Laskettavat kohteet:
    arcpy.AddLocations_na(Nimi, "Facilities", Facilities, "", "1000 Meters", "", "", "MATCH_TO_CLOSEST", "CLEAR", "NO_SNAP", "5 Meters", "EXCLUDE", "")
    arcpy.SetProgressorPosition(70)
    msg("Lis�t��n palvelualueet kartalle")

    #Piirret��n Layer kartalle:
    AddLyr = arcpy.mapping.Layer(Nimi)
    Group = "Service Areas"
    AddLayerToGroup(AddLyr, Group)
    arcpy.SetProgressorPosition(90)
    
    #Suoritetaan Service Area laskenta:
    arcpy.Solve_na(Nimi)
    arcpy.SetProgressorPosition(90)
    
    Valmis()

#Poistetaan k�ytetyt facilityt:
try:
    for facility in FaciList[0]:

        if gdbCheck == False:
            facility = temp + "\\" + facility + ".shp"
        else:
            facility = temp + "\\" + facility
        ExDel(facility)
except:
    True
ExDel(Kantis)
ExDel(Kantakaupunki)
ExDel(FacilitiesProj)

##################################################################################################
#Luodaan loki-tiedosto ajon parametreist� samaan sijaintiin johon tulostiedostokin muodostetaan
##################################################################################################

msg("----------------------------")
logPath = os.path.join(temp, "SERVICE-AREA_LOGFILE_" + Nimi + ".txt")

try:
    log = open(logPath, 'w')
    log.write("LOKITIEDOSTO LASKENNAN PARAMETREISTA SERVICE AREALLE: %s\n\nLaskettavat kohteet: %s\nKaytetty Network Dataset: %s\nKaytetty Digiroad tieverkosto: %s\n\nImpedanssi: %s\nPalvelualueen raja-arvot: %s\nPysakointi tyyppi: %s\nKavely nopeus: %s\nLaskennan suunta: %s\nPiirron tarkkuus: %s\nService area p��llekk�isyys: %s\nPolygonien trimmaus: %s\nTrimmaus cut-off arvo: %s" % (str(Nimi),Facilities.encode('utf-8'),NetworkData.encode('utf-8'),LiikenneElementti.encode('utf-8'),str(Impedanssi),str(Breaks),str(Pysakointi),str(Kavely),str(Suunta),str(Details),str(Overlap),str(Trim),str(TrimCut)))
    log.close()
    msg("Kirjoitetaan lokitiedosto.")
except:
    msg("ATTENTION: Loki-tiedostoa ei luotu.")

arcpy.SetProgressorPosition(100)    

