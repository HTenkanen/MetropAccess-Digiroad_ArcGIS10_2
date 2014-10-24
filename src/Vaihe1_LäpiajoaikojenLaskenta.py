# -*- coding: iso-8859-1 -*-
#------------------------------
# METROPACCESS-DIGIROAD
# MetropAccess-tutkimushanke
# HELSINGIN YLIOPISTO
# Koodi: Henrikki Tenkanen
#-------------------------------
# 1. Läpiajoaikojen laskenta
#-------------------------------

####################################################################################
#MetropAccess-Digiroad, työkalu Digiroad-aineiston muokkaukseen MetropAccess-hankkeen menetelmän mukaisesti
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

import arcpy, sys, time, os
from arcpy import env

# Tarvittavat Tiedostot:
LiikenneElementti = arcpy.GetParameterAsText(0)
Segmentti = arcpy.GetParameterAsText(1)

#--------------------------

#Määritetään työskentelyhakemistoksi LiikenneElementin kansio:
Workspace = os.path.dirname(LiikenneElementti)
env.workspace = Workspace

#--------------------------

#Metodit:
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

#--------------------------

#Infot:
msg("------------------------------")
msg("METROPACCESS-DIGIROAD")
msg("MetropAccess-tutkimushanke")
msg("HELSINGIN YLIOPISTO")
msg("-------------------------------")
msg("1. Läpiajoaikojen laskenta")
msg("-------------------------------")

time.sleep(2.5)

#------------------------------------------
#Infot tiedostoista:
#------------------------------------------

#Segmentti:
desc = arcpy.Describe(Segmentti)
SegNimi = desc.baseName
SegType = desc.extension #Haetaan Liikenne_Segmentti-tiedoston tyyppi
SegVarmistus = SegNimi + ".shp"

if SegType == "shp":
    SegSR = desc.spatialReference.factoryCode #Spatial Reference
    
if SegType == "dbf":
    if arcpy.Exists(SegVarmistus): #Varmistetaan, että käytetään Segmentti-shapefilea, jos vain mahdollista (=tarkempi)
        SegType = "shp"
        TiedVaihto = Segmentti[:-3]
        Segmentti = TiedVaihto + "shp"
        msg("Vaihdettiin Segmentti-tiedosto dbf:stä shapefileksi.")
    else:
        msg("ERROR: Työkalu vaatii Digiroadin K-toimitusmuotoisen datan toimiakseen.")
        sys.exit()
        
SegFields = [f.name for f in arcpy.ListFields(Segmentti)]  #Katsotaan attribuutit
del desc

#............

#LiikenneElementti:

desc = arcpy.Describe(LiikenneElementti)
DigNimi = desc.baseName
LESR = desc.spatialReference.factoryCode #Spatial Reference
LEFields = [f.name for f in arcpy.ListFields(LiikenneElementti)] #Katsotaan attribuutit
del desc


#------------------------------------------
# Projektion määrittäminen
#------------------------------------------

sr = arcpy.SpatialReference()
sr.factoryCode = 104129 #GCS_EUREF_FIN
sr.create()

if SegType == "shp":   #Tarkistetaan projektio, jos kyseessä segmentti shapefile
    if SegSR == 0:     #Jos ei ole projektiota määritetty, niin määritetään se GCS_EUREF_FIN:iin
        arcpy.DefineProjection_management(Segmentti, sr)
        msg("Segmentti-tiedoston projektio määritettiin GCS_EUREF_FIN:iin")
if LESR == 0:                       #Jos ei ole projektiota määritetty, niin määritetään se GCS_EUREF_FIN:iin
    arcpy.DefineProjection_management(LiikenneElementti, sr)
    msg("Liikenne_Elementti-tiedoston projektio määritettiin GCS_EUREF_FIN:iin")

if LESR == 3067 or LESR == 2391 or LESR == 2392 or LESR == 2393 or LESR == 2394 or LESR == 104129:
    msg("Tarkistettiin liikenneverkon projektio.")
else:
    virhe("Tieverkkoaineiston tulee olla projisoituna joko EUREF_FIN_TM35FIN:iin, GCS_EUREF_FIN:iin tai Finland_Zone_2 tai -3:een (KKJ). Muuta Liikenne_elementti.shp projektio johonkin näistä (Project -työkalulla) ja aja työkalu uudelleen.")


#------------------------------------------
#LASKETAAN NOPEUSRAJOITUKSET JA LÄPIAJOAJAT
#------------------------------------------

msg("Lisätään tarvittavat kentät Liikenne_Elementti tauluun")
arcpy.SetProgressor("step", "LÄPIAJOAIKOJEN LASKENTA...Lisätään tarvittavat kentät Liikenne_Elementti tauluun...", 0, 100, 10) #Luodaan suoritusinfopalkki
Aloitus()

#Lisätään tarvittavat kentät:
arcpy.AddField_management(LiikenneElementti, "KmH", "SHORT", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(LiikenneElementti, "Pituus", "DOUBLE", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
arcpy.SetProgressorPosition(5)
arcpy.AddField_management(LiikenneElementti, "Digiroa_aa", "DOUBLE", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(LiikenneElementti, "Kokopva_aa", "DOUBLE", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
arcpy.SetProgressorPosition(10)
arcpy.AddField_management(LiikenneElementti, "Keskpva_aa", "DOUBLE", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(LiikenneElementti, "Ruuhka_aa", "DOUBLE", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(LiikenneElementti, "DynTyyppi", "LONG", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(LiikenneElementti, "DynArvo", "LONG", "", "", "", "", "NON_NULLABLE", "NON_REQUIRED", "")
arcpy.SetProgressorPosition(15)
arcpy.AddField_management(LiikenneElementti, "JuncType", "LONG")
arcpy.AddField_management(LiikenneElementti, "JuncType2", "LONG")
arcpy.AddField_management(LiikenneElementti, "JuncType3", "LONG")
arcpy.AddField_management(LiikenneElementti, "JuncType4", "LONG")
arcpy.AddField_management(LiikenneElementti, "JuncType5", "LONG")

Valmis()
arcpy.SetProgressorPosition(20)

#--------------------------

#Tehdään Digiroadista Feature Layer:
DigiFeat = "DigiFeat"
ExDel(DigiFeat)
    
arcpy.MakeFeatureLayer_management(LiikenneElementti, DigiFeat, "", "")

arcpy.SetProgressorPosition(25)
#--------------------------

#Tehdään Join LiikenneElementtien ja Segmenttien välillä:
if SegType == "shp": #Join jos data K-muodossa
    if "K_ELEM_ID" in LEFields and "K_ELEM_ID" in SegFields:
        arcpy.AddJoin_management(DigiFeat, "K_ELEM_ID", Segmentti, "K_ELEM_ID", "KEEP_COMMON")
    else:
        arcpy.AddError("Digiroad_Elementti.shp -tiedostosta tai Digiroad_Segmentti.shp -tiedostosta ei löydy tarvittavaa kenttää 'K_ELEM_ID'")
        sys.exit()
else:
    arcpy.AddError("Digiroad_Elementti.shp -tiedostosta tai Digiroad_Segmentti.shp -tiedostosta ei löydy tarvittavaa kenttää 'K_ELEM_ID'. Työkalu vaatii Digroad K-toimitusmuotoisen datan.")
    sys.exit()

arcpy.SetProgressorPosition(30)

#--------------------------

msg("Lasketaan Nopeusrajoitukset ja läpiajoajat")
Aloitus()
arcpy.SetProgressorLabel("LÄPIAJOAIKOJEN LASKENTA...Lasketaan nopeusrajoitukset ja läpiajoajat...")

#Haetaan tarvittavat tiedot Segmentti taulusta:
DynType = "[" + SegNimi + ".DYN_TYYPPI]"
ArvoSnimi = "[" + SegNimi + ".DYN_ARVO]"

arcpy.CalculateField_management(DigiFeat, "DynTyyppi", DynType, "VB", "")
arcpy.SetProgressorPosition(35)
arcpy.CalculateField_management(DigiFeat, "DynArvo", ArvoSnimi, "VB", "")

arcpy.SetProgressorPosition(40)

#Poistetaan Join:
arcpy.RemoveJoin_management(DigiFeat, SegNimi)

#Lasketaan Nopeusrajoitukset ja läpiajoajat:
arcpy.CalculateField_management(DigiFeat, "KmH", "KmHCalc(!DynTyyppi!,!DynArvo!)", "PYTHON_9.3", "def KmHCalc(tyyppi, arvo):\\n    if tyyppi == 11:\\n        return arvo\\n    else:\\n        return 0")
arcpy.SetProgressorPosition(45)
arcpy.CalculateField_management(LiikenneElementti, "KmH", "SpeedLimits(!KmH!,!TOIMINNALL!)", "PYTHON_9.3", "def SpeedLimits(kmh,toiminnall):\\n    if kmh == 0 and toiminnall == 1:\\n        return 90\\n    elif kmh == 0 and toiminnall == 2:\\n        return 80\\n    elif kmh == 0 and (toiminnall == 3 or toiminnall == 4):\\n        return 50\\n    elif kmh == 0 and (toiminnall == 5 or toiminnall == 6):\\n        return 40\\n    elif kmh == 0 and toiminnall == 10:\\n        return 4\\n    else:\\n        return kmh")
arcpy.SetProgressorPosition(50)
arcpy.CalculateField_management(LiikenneElementti, "Pituus", "!shape.length@meters!", "PYTHON_9.3", "")
arcpy.SetProgressorPosition(55)
arcpy.CalculateField_management(LiikenneElementti, "Digiroa_aa", "DigiCalc(!Pituus!,!KmH!)", "PYTHON_9.3", "def DigiCalc(pituus,kmh):\\n    if pituus == 0:\\n        return 0\\n    else:\\n        return (pituus / (kmh / 3.6)) / 60\\n\\n\\n")

Valmis()
arcpy.SetProgressorPosition(60)
msg("----------------------")

#-----------------------------------------------------
#LUODAAN LIIKENNEVALOSEGMENTTI:
#-----------------------------------------------------
msg("Luodaan liikennevalosegmentti 3. työvaihetta varten")
Aloitus()
arcpy.SetProgressorLabel("LÄPIAJOAIKOJEN LASKENTA...Luodaan liikennevalosegmentti...")
arcpy.SetProgressorPosition(65)

#Tehdään valinta, Segmentti-shapefile:
if SegType == "shp": #Select jos data K-muodossa

    Liikennevalosegmentti = "Liikennevalosegmentti.shp"
    ExDel(Liikennevalosegmentti)

    arcpy.Select_analysis(Segmentti, Liikennevalosegmentti, "\"DYN_TYYPPI\" = 9")
    arcpy.SetProgressorPosition(70)
        
#--------------------
#Deletoidaan turhat tiedostot:
arcpy.DeleteField_management(LiikenneElementti, "DynArvo")
arcpy.SetProgressorPosition(80)

Dyn9LE = "Dyn9LE.dbf"
SelectDyn9dbf = "Dyn9.dbf"
ExDel(Dyn9LE)
ExDel(SelectDyn9dbf)

#--------------------
#Luodaan geodatabase
msg("Luodaan geodatabase...")
gdbName = "MetropAccess_Digiroad.gdb"
if not arcpy.Exists(gdbName): #Luodaan uusi geodatabase ainoastaan jos sitä ei ole jo olemassa
    arcpy.CreateFileGDB_management(Workspace,gdbName, "CURRENT")

featureDS = "MetropAccess_NetworkDataset"

gdbFullPath = os.path.join(Workspace, gdbName)
arcpy.CreateFeatureDataset_management(gdbFullPath,featureDS, LiikenneElementti)

arcpy.SetProgressorPosition(90)

outFDS = os.path.join(gdbFullPath, featureDS)

#------------------
#Viedään tarvittavat datat geodatabaseen laskennan nopeuttamiseksi
msg("Viedään datat geodatabaseen...")
arcpy.FeatureClassToFeatureClass_conversion(Liikennevalosegmentti, outFDS, "LiikennevaloSegmentti")
arcpy.FeatureClassToFeatureClass_conversion(LiikenneElementti, outFDS, "METROPACCESS_DIGIROAD_LIIKENNE_ELEMENTTI")

Valmis()
arcpy.SetProgressorPosition(100)
msg("----------------------")
msg("VALMIS! Tee seuraavaksi Network Dataset työvaiheessa 2.")    
msg("----------------------")

