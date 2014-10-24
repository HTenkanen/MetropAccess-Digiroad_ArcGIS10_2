# -*- coding: cp1252 -*-

#------------------------------
# METROPACCESS-DIGIROAD
# MetropAccess-tutkimushanke
# HELSINGIN YLIOPISTO
# Koodi: Henrikki Tenkanen
#-------------------------------
# 2. Network Datasetin luonti (ohjeistus)
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

import webbrowser,os,sys,arcpy

def msg(Message):
    arcpy.AddMessage(Message)

def virhe(Virheilmoitus):
    arcpy.AddError(Virheilmoitus)
    sys.exit()

msg("------------------------------")
msg("METROPACCESS-DIGIROAD")
msg("MetropAccess-tutkimushanke")
msg("HELSINGIN YLIOPISTO")
msg("-------------------------------")
msg("2. Network Datasetin luonti (ohjeistus)")
msg("-------------------------------")

msg("Aukaistaan ohjeet Network Datasetin luontiin")

#Aikaistaan ohjeet netist� (oletus):
try:
    os.startfile('http://blogs.helsinki.fi/saavutettavuus/files/2014/01/MetropAccess_Digiroad_NetworkDatasetin_Luominen_tarkka_2014.pdf')
    os.startfile('http://blogs.helsinki.fi/saavutettavuus/files/2014/01/MetropAccess_Digiroad_NetworkDatasetin_Luominen_flow_2014.pdf')
except:
    
    #Haetaan skriptin sijainti
    scriptPath = os.path.dirname(os.path.realpath(sys.argv[0]))

    #Haetaan ohjekansion sijainti
    helpDocs = os.path.join(os.path.dirname(os.path.dirname(scriptPath)),"Dokumentaatio")
    if os.path.isdir(helpDocs):
        flow = os.path.join(helpDocs, "MetropAccess_Digiroad_NetworkDatasetin_Luominen_flow_2014.pdf")
        tarkka = os.path.join(helpDocs, "MetropAccess_Digiroad_NetworkDatasetin_Luominen_tarkka_2014.pdf")
        os.startfile(tarkka)
        os.startfile(flow)
    else:
        virhe("Selainta ei l�ytynyt! Mene manuaalisesti osoitteeseen: 'http://blogs.helsinki.fi/saavutettavuus/files/2014/01/MetropAccess_Digiroad_NetworkDatasetin_Luominen_tarkka_2014.pdf' tai 'http://blogs.helsinki.fi/saavutettavuus/files/2014/01/MetropAccess_Digiroad_NetworkDatasetin_Luominen_flow_2014.pdf'")

