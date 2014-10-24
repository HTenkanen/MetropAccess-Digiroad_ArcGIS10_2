# -*- coding: iso-8859-1 -*-
#------------------------------
# METROPACCESS-DIGIROAD
# MetropAccess-tutkimushanke
# HELSINGIN YLIOPISTO
# Koodi: Henrikki Tenkanen
#-------------------------------
# 3. Aikasakkojen laskenta
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

import arcpy, os, sys, time, string
from arcpy import env

# Tarkistetaan tarvittavat Lisenssit
arcpy.CheckOutExtension("Network")

#METODIT:

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

def ExDel(haettava):
    if arcpy.Exists(haettava):
        arcpy.Delete_management(haettava)

#---------------------------------
# Tarvittavat tiedostot ja ty�skentelyhakemistot:
NetworkData = arcpy.GetParameterAsText(0)

#Parsitaan loppujen tarvittavien tiedostojen nimet ja sijainti:
desc = arcpy.Describe(NetworkData)
NDPath = desc.path
LiikenneElementit = os.path.join(NDPath, desc.edgeSources[0].name) #Parsitaan Liikenne_Elementti -tiedoston polku ja nimi
LiikenneJunctions = os.path.join(NDPath, desc.junctionSources[0].name) #Parsitaan Junctions -tiedoston polku ja nimi
#--------------------------------

#M��ritet��n workspace:
LiikennevaloDir = os.path.dirname(LiikenneElementit)
env.workspace = LiikennevaloDir

#Luodaan FeatureDataset laskentadatoille (ArcGIS bugittaa jos n�in ei tehd�)
featureDS = "Calculations"
prjFile = LiikenneElementit[:-4] + ".prj"
gdbPath = os.path.dirname(LiikennevaloDir)
Workspace = gdbPath
scratchWorkspace = os.path.dirname(gdbPath)
calcPath = os.path.join(gdbPath, featureDS)

if not arcpy.Exists(calcPath):
    arcpy.CreateFeatureDataset_management(gdbPath,featureDS, LiikenneElementit)

if not arcpy.Exists(LiikenneJunctions): #Tarkistetaan, ett� Junctions.shp tiedosto l�ytyy
    teksti = "Tiedostoa " + LiikenneJunctions + " ei l�ydy! Tarkista, ett� kansiosta, jossa sijaitsee k�ytt�m�si Network Dataset l�ytyy my�s pistetiedosto seuraavassa kirjoitusmuodossa: '<Nime�m�siNetworkDataset>_ND_Junctions.shp'."
    virhe(teksti)


Liikennevalosegmentti = "Liikennevalosegmentti"
if arcpy.Exists(Liikennevalosegmentti): #Tarkistetaan, ett� Liikennevalosegmentti.shp tiedosto l�ytyy
    Liikennevalosegmentti = os.path.join(LiikennevaloDir,"Liikennevalosegmentti")
else:
    teksti = "ERROR: Tarvittavaa tiedostoa 'Liikennevalosegmentti' ei l�ydy! Suorita 1. ty�vaihe uudelleen tai siirr� Liikennevalosegmentti-tiedosto haluttuun kansioon (alla) ja palaa sen j�lkeen suorittamaan t�m� ty�vaihe."
    tempSijainti = "Tiedostoa etsittiin kansiosta: " + LiikennevaloDir
    msg(teksti)
    msg(tempSijainti)
    sys.exit()

#Katsotaan NetworkDatan attribuutit:
attributes = desc.attributes
NDparams = []
for attribute in attributes:
    NDparams.append(attribute.name)
del desc
del attributes

#-----------------------------------------------------
#Katsotaan Liikenne_Elementti -tiedoston attribuutit:
LEparams = [f.name for f in arcpy.ListFields(LiikenneElementit)]

#Tarkistetaan, ett� tarvittavat muuttujat l�ytyv�t Liikenne_elementti -tiedostosta:
if not "Pituus" in LEparams:
    virhe("Attribuuttia 'Pituus' ei l�ydy k�ytett�v�st� Liikenne_Elementti.shp tiedostosta. Tarkista, ett� tie-elementin pituuden m��ritt�v� attribuutti on nimetty nimell� 'Pituus'")
if not "KmH" in LEparams:
    virhe("Attribuuttia 'KmH' ei l�ydy k�ytett�v�st� Liikenne_Elementti.shp tiedostosta. Tarkista, attribuutti on nimetty kirjoitusasulla 'KmH'")    
if not "Digiroa_aa" in LEparams:
    virhe("Attribuuttia 'Digiroa_aa' ei l�ydy k�ytett�v�st� Liikenne_Elementti.shp tiedostosta. Tarkista, ett� attribuutti on nimetty kirjoitusasulla 'Digiroa_aa'")
if "KokoPva_aa" or "Kokopva_aa" in LEparams:
    True
else:
    virhe("Attribuuttia 'Kokopva_aa' ei l�ydy k�ytett�v�st� Liikenne_Elementti.shp tiedostosta. Tarkista, ett� attribuutti on nimetty kirjoitusasulla 'Kokopva_aa'")
if not "Keskpva_aa" in LEparams:
    virhe("Attribuuttia 'Keskpva_aa' ei l�ydy k�ytett�v�st� Liikenne_Elementti.shp tiedostosta. Tarkista, ett� attribuutti on nimetty kirjoitusasulla 'Keskpva_aa'")
if not "Ruuhka_aa" in LEparams:
    virhe("Attribuuttia 'Ruuhka_aa' ei l�ydy k�ytett�v�st� Liikenne_Elementti.shp tiedostosta. Tarkista, ett� attribuutti on nimetty kirjoitusasulla 'Ruuhka_aa'")
if not "JuncType" in LEparams:
    virhe("Attribuuttia 'JuncType' ei l�ydy k�ytett�v�st� Liikenne_Elementti.shp tiedostosta. Tarkista, ett� attribuutti on nimetty kirjoitusasulla 'JuncType'")
if not "JuncType2" in LEparams:
    virhe("Attribuuttia 'JuncType2' ei l�ydy k�ytett�v�st� Liikenne_Elementti.shp tiedostosta. Tarkista, ett� attribuutti on nimetty kirjoitusasulla 'JuncType2'")
if not "JuncType3" in LEparams:
    virhe("Attribuuttia 'JuncType3' ei l�ydy k�ytett�v�st� Liikenne_Elementti.shp tiedostosta. Tarkista, ett� attribuutti on nimetty kirjoitusasulla 'JuncType3'")
if not "JuncType4" in LEparams:
    virhe("Attribuuttia 'JuncType4' ei l�ydy k�ytett�v�st� Liikenne_Elementti.shp tiedostosta. Tarkista, ett� attribuutti on nimetty kirjoitusasulla 'JuncType4'")
if not "JuncType5" in LEparams:
    virhe("Attribuuttia 'JuncType5' ei l�ydy k�ytett�v�st� Liikenne_Elementti.shp tiedostosta. Tarkista, ett� attribuutti on nimetty kirjoitusasulla 'JuncType5'")


#Tarkistetaan, ett� tarvittavat muuttujat l�ytyv�t Network Datasetist�:
if not "Pituus" in NDparams:
    virhe("Attribuuttia 'Pituus' ei l�ydy k�ytett�v�st� Network Datasetist�. Tarkista, ett� tie-elementin pituuden m��ritt�v� attribuutti on nimetty nimell� 'Pituus'")
if not "Digiroa_aa" in NDparams:
    virhe("Attribuuttia 'Digiroa_aa' ei l�ydy k�ytett�v�st� Network Datasetist�. Tarkista, ett� attribuutti on nimetty kirjoitusasulla 'Digiroa_aa'")
if "KokoPva_aa" or "Kokopva_aa" in NDparams:
    True
else:
    virhe("Attribuuttia 'Kokopva_aa' ei l�ydy k�ytett�v�st� Network Datasetist�. Tarkista, ett� attribuutti on nimetty kirjoitusasulla 'Kokopva_aa'")
if not "Keskpva_aa" in NDparams:
    virhe("Attribuuttia 'Keskpva_aa' ei l�ydy k�ytett�v�st� Network Datasetist�. Tarkista, ett� attribuutti on nimetty kirjoitusasulla 'Keskpva_aa'")
if not "Ruuhka_aa" in NDparams:
    virhe("Attribuuttia 'Ruuhka_aa' ei l�ydy k�ytett�v�st� Network Datasetist�. Tarkista, ett� attribuutti on nimetty kirjoitusasulla 'Ruuhka_aa'")

#--------------------------------------------------
#TARKISTETAAN PROJEKTIO
#--------------------------------------------------

desc = arcpy.Describe(LiikenneElementit)
Projektio = desc.spatialReference.factoryCode
if Projektio in [3067,2391,2392,2393,2394,104129]: #== 3067 or Projektio == 2391 or Projektio == 2392 or Projektio == 2393 or Projektio == 2394 or Projektio == 104129:
    msg("Tarkistettiin liikenneverkon projektio.")
else:
    virhe("Tieverkkoaineiston tulee olla projisoituna joko EUREF_FIN_TM35FIN:iin, GCS_EUREF_FIN:iin tai Finland_Zone_1, 2, 3 tai -4:��n (KKJ). Muuta Liikenne_elementti.shp projektio johonkin n�ist� Project -ty�kalulla, luo uusi Network Dataset perustuen t�h�n uuteen projisoituun LiikenneElementti -tiedostoon ja aja ty�kalu uudelleen.")

del desc
#--------------------------------------------------
#Infot:
msg("------------------------------")
msg("METROPACCESS-DIGIROAD")
msg("MetropAccess-tutkimushanke")
msg("HELSINGIN YLIOPISTO")
msg("-------------------------------")
msg("3. Aikasakkojen Laskenta")
msg("-------------------------------")

time.sleep(2.5)
#------------------------------------------------------------------------------------------------------------------------------
#MUODOSTETAAN LIIKENNEVALOPISTEET ODC:LLA (CutOff 20 metri�)
#------------------------------------------------------------------------------------------------------------------------------
msg("M��ritet��n tie-elementit, joihin vaikuttaa liikennevalot")
Aloitus()
arcpy.SetProgressor("step", "AIKASAKKOJEN LASKENTA...M��ritet��n tie-elementit, joihin vaikuttavat liikennevalot...", 0, 100, 10) #Luodaan suoritusinfopalkki

#Tehd��n Liikennevalosegmenteist� pistemuotoinen:
LVSpoint = os.path.join(LiikennevaloDir,"LiikennevaloSegmenttiPoint")
ExDel(LVSpoint)
arcpy.FeatureToPoint_management(Liikennevalosegmentti, LVSpoint, "CENTROID")
arcpy.SetProgressorPosition(5)

#Importataan datat Calculations-datasettiin
LiikennevaloPisteet = "LiikennevaloPisteet"
Junctions = "Junctions"

LVPcheck = os.path.join(calcPath, LiikennevaloPisteet)
JunctionsCheck = os.path.join(calcPath, Junctions)

ExDel(LVPcheck)
ExDel(JunctionsCheck)

arcpy.FeatureClassToFeatureClass_conversion(LiikenneJunctions, calcPath, Junctions)
arcpy.FeatureClassToFeatureClass_conversion(LVSpoint, calcPath, LiikennevaloPisteet)

ExDel(LVSpoint)

LVSpoint = os.path.join(calcPath, LiikennevaloPisteet)
LiikenneJunctions = os.path.join(calcPath, Junctions)

#Haetaan Near analyysilla Junction-pisteist� sellaiset kohteet, jotka ovat 20 metrin sis�ll� Liikennevaloista (jotta saadaan Destination pisteiden m��r�� pienennetty� ODC:hen)
arcpy.Near_analysis(LiikenneJunctions, LVSpoint, "20 Meters", "NO_LOCATION", "NO_ANGLE")

#Tehd��n t�st� Feature-Layer:
LVJ = "LiikennevalojenLaheisyydessaOlevatJunctionit"
ExDel(LVJ) #Tarkistetaan p��llekk�isyys
arcpy.MakeFeatureLayer_management(LiikenneJunctions, LVJ, """NEAR_FID <> -1""", "")

arcpy.SetProgressorPosition(10)

ODC = "KAIKKILiikenneValot"
ExDel(ODC)

if "Hierarkia" in NDparams:
    Hierarkia = "USE_HIERARCHY"
else:
    Hierarkia = "NO_HIERARCHY"


#Tehd��n OD-Cost-Matrix Layer ja LASKETAAN VAIN kohteet, jotka ovat 20 metrin p��ss� Origineista:
msg("Luodaan ODC-Cost-Matrix. Haetaan tie-elementit 20m liikennevaloista.")
Aloitus()
arcpy.SetProgressor("step", "Luodaan OD-Cost-Matrix...Haetaan tie-elementit 20m liikennevaloista...", 0, 100, 25) #Luodaan suoritusinfopalkki
arcpy.MakeODCostMatrixLayer_na(NetworkData, ODC, "Pituus", "20", "", "", "ALLOW_DEAD_ENDS_ONLY", "", Hierarkia, "", "STRAIGHT_LINES")
arcpy.SetProgressorPosition(20)
Valmis()

#Origineiksi m��ritell��n Liikennevalosegmentit(pistemuotoisena):
msg("Lis�t��n OD-Cost-Matriisiin L�ht�pisteet")
Aloitus()
arcpy.SetProgressorLabel("Lis�t��n OD-Cost-Matriisiin L�ht�pisteet...T�ss� menee hetki...")
arcpy.AddLocations_na(ODC, "Origins", LVSpoint, "Name FID #", "10 Meters", "", "", "MATCH_TO_CLOSEST", "CLEAR", "NO_SNAP", "5 Meters", "EXCLUDE", "")
arcpy.SetProgressorPosition(30)
Valmis()

#Destinationeiksi m��ritell��n kaikki Junctionit, jotka ovat 20 metrin p��ss� LiikennevaloSegmenteist�:
msg("Lis�t��n OD-Cost-Matriisiin Kohdepisteet")
Aloitus()
arcpy.SetProgressorLabel("Lis�t��n OD-Cost-Matriisiin Kohdepisteet...T�ss� menee hetki...")
arcpy.AddLocations_na(ODC, "Destinations", LVJ, "Name FID #", "10 Meters", "", "", "MATCH_TO_CLOSEST", "APPEND", "NO_SNAP", "5 Meters", "EXCLUDE", "")
arcpy.SetProgressorPosition(40)
Valmis()

#Suoritetaan ODC:
msg("Suoritetaan OD-Cost-Matrix")
Aloitus()
arcpy.SetProgressorLabel("Solve...")
arcpy.Solve_na(ODC, "SKIP", "TERMINATE")


#Luodaan FeatureDataset LiikenneElementeille (luodaan uniikki jos kansio jo l�ytyy Workspacesta):
directory = os.path.join(Workspace,"LiikenneElementit")

if not arcpy.Exists(directory):
    arcpy.CreateFeatureDataset_management(Workspace,"LiikenneElementit", LiikenneElementit)

#M��ritet��n ODC-Layer:
Lines = ODC + "/" + "Lines"

env.workspace = directory #M��ritet��n ty�skentelyhakemisto

LV = "Liikennevalot"
ExDel(LV)
arcpy.SpatialJoin_analysis(LVJ, Lines, LV, "JOIN_ONE_TO_ONE", "KEEP_COMMON", "", "INTERSECT")

#Tehd��n my�hemmin tarvittava FeatureLayer:
LVF = "LiikenneValoFeat"
ExDel(LVF)
arcpy.MakeFeatureLayer_management(LV, LVF, "", "")

arcpy.SetProgressorPosition(100)
msg("Liikennevalot m��ritetty!")
Valmis()
msg("----------------------")
arcpy.ResetProgressor()

arcpy.SetProgressor("step", "AIKASAKKOJEN LASKENTA...M��ritet��n rampit...", 0, 100, 10)
arcpy.SetProgressorPosition(50)

#------------------------------------------------------------------------------------------------------------------------------
#MUODOSTETAAN MUUNTYYPPISET LIIKENNE-ELEMENTIT (Rampit, Kevyen Liikenteen risteykset, Tavalliset Risteykset)
#------------------------------------------------------------------------------------------------------------------------------

#Valitaan sellaiset Junctionit jotka ovat risteyksi�:
NDJunct = "NDJunct"
ExDel(NDJunct) #Tarkistetaan p��llekk�isyys
arcpy.SpatialJoin_analysis(LiikenneJunctions, LiikenneElementit, NDJunct, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "INTERSECT", "", "")
arcpy.SetProgressorPosition(45)

Risteys = "Risteys"
ExDel(Risteys) #Tarkistetaan p��llekk�isyys
arcpy.MakeFeatureLayer_management(NDJunct, Risteys, """Join_Count > 2""", "")

#------------------------------------------------------------------------------------------------------------------------------
#MUODOSTETAAN RAMPIT

msg("M��ritet��n rampit")
Aloitus()

#Valitaan Liikenne-Elementeist� segmentit, jotka ovat tyyppi� Ramppi (DynTyyppi == 8)
RampitS = "RamppiSegmentti"
ExDel(RampitS)
arcpy.MakeFeatureLayer_management(LiikenneElementit, RampitS, """DynTyyppi = 8""", "")
arcpy.SetProgressorPosition(50)

#Haetaan Tavallisista Risteyksist� ne pisteet, jotka ovat ramppeja:
Rampit = "Rampit"
ExDel(Rampit)
arcpy.SpatialJoin_analysis(Risteys, RampitS, Rampit, "JOIN_ONE_TO_ONE", "KEEP_COMMON", "", "INTERSECT", "", "")

msg("Rampit m��ritetty!")
arcpy.SetProgressorPosition(55)
Valmis()
msg("----------------------")
#------------------------------------------------------------------------------------------------------------------------------
#MUODOSTETAAN KEVYENLIIKENTEEN RISTEYKSET

msg("M��ritet��n Kevyenliikenteen risteykset")
arcpy.SetProgressorLabel("AIKASAKKOJEN LASKENTA...M��ritet��n Kevyenliikenteen risteykset...")
Aloitus()

KevytLS = "KevyenLiikenteenSegmentti"
ExDel(KevytLS)
arcpy.MakeFeatureLayer_management(LiikenneElementit, KevytLS, """TOIMINNALL = 10""", "")
arcpy.SetProgressorPosition(60)

KevytL = "KevytLiikenne"
ExDel(KevytL)
arcpy.SpatialJoin_analysis(Risteys, KevytLS, KevytL, "JOIN_ONE_TO_ONE", "KEEP_COMMON", "", "INTERSECT", "", "")

msg("Kevyenliikenteen risteykset m��ritetty!")
arcpy.SetProgressorPosition(65)
Valmis()
msg("----------------------")

#------------------------------------------------------------------------------------------------------------------------------
#MUODOSTETAAN TAVALLISET RISTEYKSET

msg("M��ritet��n tavalliset risteykset")
arcpy.SetProgressorLabel("AIKASAKKOJEN LASKENTA...M��ritet��n tavalliset risteykset...")
Aloitus()

#Valitaan Risteyksist�, pisteet jotka eiv�t ole Liikennevalollisia:
arcpy.SelectLayerByLocation_management(Risteys, "INTERSECT", LVF)
#Tehd��n Switch:
arcpy.SelectLayerByAttribute_management(Risteys, "SWITCH_SELECTION")

#Tehd��n t�st� oma tiedosto:
TVR1F = "TavallisetRisteyksetF1"
ExDel(TVR1F)
arcpy.MakeFeatureLayer_management(Risteys, TVR1F, "", "")

#............................

#Valitaan n�ist�, pisteet jotka eiv�t ole ramppeja:
arcpy.SelectLayerByLocation_management(TVR1F, "INTERSECT", Rampit)
#Tehd��n Switch:
arcpy.SelectLayerByAttribute_management(TVR1F, "SWITCH_SELECTION")

#Tehd��n t�st� oma tiedosto:
TVR2F = "TavallisetRisteyksetF2"
ExDel(TVR2F)
arcpy.MakeFeatureLayer_management(TVR1F, TVR2F, "", "")
arcpy.SetProgressorPosition(70)
#.............................

#Valitaan n�ist�, pisteet jotka eiv�t ole Kevyen Liikenteen risteyksi�:
arcpy.SelectLayerByLocation_management(TVR2F, "INTERSECT", KevytL)
#Tehd��n Switch:
arcpy.SelectLayerByAttribute_management(TVR2F, "SWITCH_SELECTION")

#Tehd��n t�st� oma tiedosto:
TVR3F = "TavallisetRisteyksetF3"
ExDel(TVR3F)
arcpy.MakeFeatureLayer_management(TVR2F, TVR3F, "", "")

#............................

#MUODOSTETAAN TAVALLISET RISTEYKSET LAYER WORKSPACEEN
TVR = "TavallisetRisteykset"
ExDel(TVR)
arcpy.Select_analysis(TVR3F, TVR)

msg("Tavalliset risteykset m��ritetty!")
arcpy.SetProgressorPosition(75)
Valmis()
msg("----------------------")
#Poistetaan turhat tiedostot joita on t�h�n menness� syntynyt:
ExDel(ODC)
ExDel(LVJ)
ExDel(LVSpoint)
ExDel(LVF)
ExDel(NDJunct)
ExDel(Risteys)
ExDel(RampitS)
ExDel(KevytLS)
ExDel(TVR1F)
ExDel(TVR2F)
ExDel(TVR3F)
ExDel(JunctionsCheck)
ExDel(calcPath)
ExDel(Liikennevalosegmentti)

#------------------------------------------------------------------------------------------------------------------------------
#LASKETAAN LIIKENNE-ELEMENTEILLE TIEDOT SIIT�, MINK�TYYPPISI� RISTEYKSI� KUHUNKIN ELEMENTTII KOHDISTUU
#------------------------------------------------------------------------------------------------------------------------------

msg("M��ritet��n tie-elementeille tieto siit�, mink�tyyppisi� risteyksi� kuhunkin tie-elementtiin kohdistuu")
arcpy.SetProgressorLabel("AIKASAKKOJEN LASKENTA...M��ritet��n elementteihin kohdistuvat risteystyypit...")
Aloitus()

#Tehd��n LiikenneElementti FeatureLayer:
LEF = "LiikenneElementtiF"
ExDel(LEF)
arcpy.MakeFeatureLayer_management(LiikenneElementit, LEF, "", "")

#M��ritet��n Tie-Elementit, jotka ovat Liikennevalojen vaikutuksen alaisia:
arcpy.SelectLayerByLocation_management(LEF, "INTERSECT", LV, "", "NEW_SELECTION")
#Ei oteta Kevyen Liikenteen segmenttej� huomioon:
arcpy.SelectLayerByAttribute_management(LEF, "SUBSET_SELECTION", "\"TOIMINNALL\" <>10")
#Otetaan vain liikennevalosegmentit huomioon:
arcpy.SelectLayerByAttribute_management(LEF, "SUBSET_SELECTION", "\"DynTyyppi\" = 9") 
#Lasketaan JuncType arvoksi 1:
arcpy.CalculateField_management(LEF, "JuncType", "1", "PYTHON")
arcpy.SetProgressorPosition(80)

#M��ritet��n Tie-Elementit, jotka ovat Tavallisten risteysten vaikutuksen alaisia:
arcpy.SelectLayerByLocation_management(LEF, "INTERSECT", TVR, "", "NEW_SELECTION")
#Ei oteta Kevyen Liikenteen segmenttej� huomioon:
arcpy.SelectLayerByAttribute_management(LEF, "SUBSET_SELECTION", "\"TOIMINNALL\" <>10")
#Lasketaan JuncType2 arvoksi 1:
arcpy.CalculateField_management(LEF, "JuncType2", "1", "PYTHON")

#M��ritet��n Tie-Elementit, jotka ovat Ramppien vaikutuksen alaisia:
arcpy.SelectLayerByLocation_management(LEF, "INTERSECT", Rampit, "", "NEW_SELECTION")
#Otetaan vain TYYPPI = 8 huomioon(ramppi):
arcpy.SelectLayerByAttribute_management(LEF, "SUBSET_SELECTION", "\"TYYPPI\" =8")
#Lasketaan JuncType3 arvoksi 1:
arcpy.CalculateField_management(LEF, "JuncType3", "1", "PYTHON")

#M��ritet��n Tie-Elementit, jotka ovat Kevyen Liikenteen v�ylien vaikutuksen alaisia:
arcpy.SelectLayerByLocation_management(LEF, "INTERSECT", KevytL, "", "NEW_SELECTION")
#Ei oteta Kevyen Liikenteen segmenttej� huomioon:
arcpy.SelectLayerByAttribute_management(LEF, "SUBSET_SELECTION", "\"TOIMINNALL\" <>10")
#Lasketaan JuncType4 arvoksi 1:
arcpy.CalculateField_management(LEF, "JuncType4", "1", "PYTHON")

#LASKETAAN N�M� KAIKKI YHTEEN
arcpy.CalculateField_management(LiikenneElementit, "JuncType5", "!JuncType! + !JuncType2! + !JuncType3! + !JuncType4!", "PYTHON")

msg("Elementteihin kohdistuvat risteystyypit m��ritetty!")
arcpy.SetProgressorPosition(85)
Valmis()
msg("----------------------")

#------------------------------------------------------------------------------------------------------------------------------
#LASKETAAN LIIKENNE-ELEMENTEILLE AIKASAKOT
#------------------------------------------------------------------------------------------------------------------------------

msg("Lasketaan Liikenne-elementeille aikasakot")
arcpy.SetProgressorLabel("AIKASAKKOJEN LASKENTA...Lasketaan aikasakot...")
Aloitus()

#Aikasakot:
Keskiarvo12 = 11.311 / 60
Keskiarvo3 = 9.439 / 60
Keskiarvo456 = 9.362 / 60

Paiva12 = 9.979 / 60
Paiva3 = 6.650 / 60
Paiva456 = 7.752 / 60

Ruuhka12 = 12.195 / 60
Ruuhka3 = 11.199 / 60
Ruuhka456 = 10.633 / 60

#HUOM tyyppi = TYYPPI ei DynTyyppi

#Luodaan datan lukija
Reader = arcpy.UpdateCursor(LiikenneElementit)

for row in Reader:
#Elementit jotka ovat Toiminnallista luokkaa 1 tai 2:    
    if row.TOIMINNALL == 1 or row.TOIMINNALL == 2:
        if row.TYYPPI == 8:                                                #Lasketaan rampeille aikasakot
            if row.JuncType3 == 1 and row.KmH < 70 and row.JuncType5 != 2: # Alle 70 kmh tie-elementti leikkaa risteykseen
                row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo12/3)
                row.Keskpva_aa = row.Digiroa_aa + (Paiva12/3)
                row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka12/2)
            elif row.KmH >=70:                                             #Lasketaan kaikille rampeille mediaanihidastuvuus
                row.Kokopva_aa = row.Digiroa_aa * 1.884662
                row.Keskpva_aa = row.Digiroa_aa * 1.667750
                row.Ruuhka_aa = row.Digiroa_aa * 2.022762
            else:
                row.Kokopva_aa = row.Digiroa_aa + ((Keskiarvo12/3)*2)
                row.Keskpva_aa = row.Digiroa_aa + ((Paiva12/4)*4)
                row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka12/2)
        elif row.JuncType5 == 0 and row.KmH >= 70:                         #Lasketaan kaikille yli 70 kmh teille 1.1 tai 1.2 kerroin. Kannattaa tarvittaessa poistaa
            row.Kokopva_aa = row.Digiroa_aa * 1.1
            row.Keskpva_aa = row.Digiroa_aa
            row.Ruuhka_aa = row.Digiroa_aa * 1.2
        elif row.JuncType == 1 or row.JuncType5 ==2:                       #Liikennevaloristeyksille ja risteyksille, mihin leikkaa kaksi risteyst� samassa tieluokassa aikasakko lasketaan aikasakko samaan tie-elementtiin 
            row.Kokopva_aa = row.Digiroa_aa + Keskiarvo12
            row.Keskpva_aa = row.Digiroa_aa + Paiva12
            row.Ruuhka_aa = row.Digiroa_aa + Ruuhka12
        elif row.TYYPPI == 4 and row.JuncType5 !=0:                        #Liikenneympyr�iss� sakotetaan vain 3/4, 2/3 tai 1/2 aikasakko
            row.Kokopva_aa = row.Digiroa_aa + ((Keskiarvo12/3)*2)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva12/2)
            row.Ruuhka_aa = row.Digiroa_aa + ((Ruuhka12/4)*3)
        elif row.JuncType3 == 1 and row.KmH < 70 and row.TYYPPI != 8 and row.JuncType5 != 2: #Tie-elementtiin, mik� liittyy toiseen tie-elementtini lasketaan 1/3 tai 1/2 aikasakko
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo12/3)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva12/4)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka12/2)
        elif row.JuncType2 == 1 or row.JuncType4 == 1 and row.JuncType5 != 2: #Normaalisti laskettavat risteykset
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo12/2)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva12/2)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka12/2)

        elif row.JuncType3 == 1 and row.KmH >= 70 and row.JuncType5 != 2:  #Yli 70 kmh teille leikkaavaan tie-elementtiin, mik� ei ole ramppi lasketaan 1/2, 1/3 tai 1/4 aikasakko
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo12/3)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva12/4)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka12/2)
        
        else:
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo12 / 4) 
            row.Keskpva_aa = row.Digiroa_aa + (Paiva12 / 4)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka12 / 4)
                    
#Elementit jotka ovat Toiminnallista luokkaa 3:        
    elif row.TOIMINNALL == 3:
        if row.TYYPPI == 8:                                                #Lasketaan rampeille aikasakot
            if row.JuncType3 == 1 and row.KmH < 70 and row.JuncType5 != 2: # Alle 70 kmh tie-elementti leikkaa risteykseen
                row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo3/3)
                row.Keskpva_aa = row.Digiroa_aa + (Paiva3/3)
                row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka3/2)
            elif row.KmH >=70:                                             #Lasketaan kaikille rampeille mediaanihidastuvuus
                row.Kokopva_aa = row.Digiroa_aa * 1.884662
                row.Keskpva_aa = row.Digiroa_aa * 1.667750
                row.Ruuhka_aa = row.Digiroa_aa * 2.022762
            else:
                row.Kokopva_aa = row.Digiroa_aa + ((Keskiarvo3/3)*2)
                row.Keskpva_aa = row.Digiroa_aa + ((Paiva3/4)*3)
                row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka3/2)
        elif row.JuncType5 == 0 and row.KmH >= 70:                         #Lasketaan kaikille yli 70 kmh teille 1.1 tai 1.2 kerroin. Kannattaa tarvittaessa poistaa
            row.Kokopva_aa = row.Digiroa_aa * 1.1
            row.Keskpva_aa = row.Digiroa_aa
            row.Ruuhka_aa = row.Digiroa_aa * 1.2
        elif row.JuncType == 1 or row.JuncType5 ==2:                       #Liikennevaloristeyksille ja risteyksille, mihin leikkaa kaksi risteyst� samassa tieluokassa aikasakko lasketaan aikasakko samaan tie-elementtiin 
            row.Kokopva_aa = row.Digiroa_aa + Keskiarvo3
            row.Keskpva_aa = row.Digiroa_aa + Paiva3
            row.Ruuhka_aa = row.Digiroa_aa + Ruuhka3
        elif row.TYYPPI == 4 and row.JuncType5 !=0:                        #Liikenneympyr�iss� sakotetaan vain 3/4, 2/3 tai 1/2 aikasakko 
            row.Kokopva_aa = row.Digiroa_aa + ((Keskiarvo3/3)*2)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva3/2)
            row.Ruuhka_aa = row.Digiroa_aa + ((Ruuhka3/4)*3)
        elif row.JuncType3 == 1 and row.KmH < 70 and row.TYYPPI != 8 and row.JuncType5 != 2: #Tie-elementtiin, mik� liittyy toiseen tie-elementtini lasketaan 1/3 tai 1/2 aikasakko
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo3/3)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva3/4)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka3/2)
        elif row.JuncType2 == 1 or row.JuncType4 == 1 and row.JuncType5 != 2: #Normaalisti laskettavat risteykset
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo3/2)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva3/2)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka3/2)
        elif row.JuncType3 == 1 and row.KmH >= 70 and row.JuncType5 != 2:  #Yli 70 kmh teille leikkaavaan tie-elementtiin, mik� ei ole ramppi lasketaan 1/2, 1/3 tai 1/4 aikasakko
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo3/3)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva3/4)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka3/2)

        else:
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo3 / 4) 
            row.Keskpva_aa = row.Digiroa_aa + (Paiva3 / 4)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka3 / 4)
                
#Elementit jotka ovat Toiminnallista luokkaa 4,5 tai 6:
    elif row.TOIMINNALL == 4 or row.TOIMINNALL == 5 or row.TOIMINNALL == 6:
        if row.TYYPPI == 8:                                                #Lasketaan rampeille aikasakot
            if row.JuncType3 == 1 and row.KmH < 70 and row.JuncType5 != 2: # Alle 70 kmh tie-elementti leikkaa risteykseen
                row.Kokopva_aa = row.Digiroa_aa + ((Keskiarvo456/3)*2)
                row.Keskpva_aa = row.Digiroa_aa + ((Paiva456/3)*4)
                row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka456/2)
            elif row.KmH >=70:                                             #Lasketaan kaikille rampeille mediaanihidastuvuus
                row.Kokopva_aa = row.Digiroa_aa * 1.884662
                row.Keskpva_aa = row.Digiroa_aa * 1.667750
                row.Ruuhka_aa = row.Digiroa_aa * 2.022762
            else:
                row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo456/3)
                row.Keskpva_aa = row.Digiroa_aa + (Paiva456/4)
                row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka456/2)
        elif row.JuncType5 == 0 and row.KmH >= 70:                         #Lasketaan kaikille yli 70 kmh teille 1.1 tai 1.2 kerroin. Kannattaa tarvittaessa poistaa
            row.Kokopva_aa = row.Digiroa_aa * 1.1
            row.Keskpva_aa = row.Digiroa_aa
            row.Ruuhka_aa = row.Digiroa_aa * 1.2
        elif row.JuncType == 1 or row.JuncType5 ==2:                       #Liikennevaloristeyksille ja risteyksille, mihin leikkaa kaksi risteyst� samassa tieluokassa aikasakko lasketaan aikasakko samaan tie-elementtiin 
            row.Kokopva_aa = row.Digiroa_aa + Keskiarvo456
            row.Keskpva_aa = row.Digiroa_aa + Paiva456
            row.Ruuhka_aa = row.Digiroa_aa + Ruuhka456
        elif row.TYYPPI == 4 and row.JuncType5 !=0:                        #Liikenneympyr�iss� sakotetaan vain 3/4, 2/3 tai 1/2 aikasakko
            row.Kokopva_aa = row.Digiroa_aa + ((Keskiarvo456/3)*2)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva456/2)
            row.Ruuhka_aa = row.Digiroa_aa + ((Ruuhka456/4)*3)
        elif row.JuncType3 == 1 and row.KmH < 70 and row.TYYPPI != 8 and row.JuncType5 != 2: #Tie-elementtiin, mik� liittyy toiseen tie-elementtini lasketaan 1/3 tai 1/2 aikasakko
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo456/3)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva456/4)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka456/2)
        elif row.JuncType2 == 1 or row.JuncType4 == 1 and row.JuncType5 != 2: #Normaalisti laskettavat risteykset
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo456/2)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva456/2)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka456/2)
        elif row.JuncType3 == 1 and row.KmH >= 70 and row.JuncType5 != 2:  #Yli 70 kmh teille leikkaavaan tie-elementtiin, mik� ei ole ramppi lasketaan 1/2, 1/3 tai 1/4 aikasakko
            row.Kokopva_aa = row.Digiroa_aa + (Keskiarvo456/3)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva456/4)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka456/2)

        else:
            row.Kokopva_aa = row.Digiroa_aa  + (Keskiarvo456 / 4)
            row.Keskpva_aa = row.Digiroa_aa + (Paiva456 / 4)
            row.Ruuhka_aa = row.Digiroa_aa + (Ruuhka456 / 4)


    else:                                                                  #Muille toiminnallisille luokille lasketaan nopeusrajoituksen mukainen l�piajoaika
        row.Kokopva_aa = row.Digiroa_aa
        row.Keskpva_aa = row.Digiroa_aa
        row.Ruuhka_aa = row.Digiroa_aa

        
    Reader.updateRow(row)
    del row
del Reader
###########################
arcpy.SetProgressorPosition(90)
#Poistetaan tiedostosta turhat kent�t:
arcpy.DeleteField_management(LiikenneElementit, "JuncType;JuncType2;JuncType3;JuncType4;JuncType5;DynTyyppi")

msg("Aikasakot laskettu!")
arcpy.SetProgressorPosition(95)
Valmis()
msg("----------------------")
msg("Build Network Dataset")
arcpy.SetProgressorLabel("AIKASAKKOJEN LASKENTA...Build Network Dataset...")
Aloitus()
#Buildataan NetworkDataset uudestaan, jolloin se on heti valmis k�ytett�v�ksi:
arcpy.BuildNetwork_na(NetworkData)
Valmis()
arcpy.SetProgressorPosition(100)

msg("----------------------")
msg("VALMIS! Nyt k�ytt�m��si Network Datasettiin on laskettu todenmukaisemmat l�piajoajat sarakkeisiin: Kokopva_aa, Keskpva_aa sek� Ruuhka_aa.")
msg("Network Dataset on nyt valmis k�ytett�v�ksi reititysanalyyseihin.")
msg("Halutessasi voit suorittaa 4. ty�vaiheen, jossa otetaan matka-ajan lis�ksi huomioon k�velyyn sek� parkkipaikan etsint��n kuluva aika (Kokonaismatkaketju).")
msg("----------------------")
