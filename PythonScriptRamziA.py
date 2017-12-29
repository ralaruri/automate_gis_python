#Ramzi Al-Aruri GGS650 Final Project#

#-------------------------Script-----------------------#

#----Part 1-----Select Analysis and Setting up Enviroment----#
#Checking Extensions and setting up the workspace
import arcpy
arcpy.CheckExtension("Network")
arcpy.CheckExtension("Spatial")
arcpy.env.workspace = "C:\\Users\\ralaruri\\Desktop\\RamziAFinal\\RamziAFinal.gdb"
outputPath = "C:\\Users\\ralaruri\\Desktop\\RamziAFinal\\Output"

#Splitting the Counties from the UScounty shapefile pulling what is needed
#Using SQL statements using the name of the county and the State FIP code of North Dakota (38)
#Also Splitting Primary roads form the North Dakota Tiger Roads Data
arcpy.Select_analysis("uscounty","CassCounty.shp",'"NAME" = \'Cass\' AND "STATEFP" = \'38\'')
arcpy.Select_analysis("uscounty","TraillCounty.shp",'"NAME" = \'Traill\' AND "STATEFP" = \'38\'')
arcpy.Select_analysis("uscounty","SteeleCounty.shp",'"NAME" = \'Steele\' AND "STATEFP" = \'38\'')
arcpy.Select_analysis("uscounty","BarnesCounty.shp",'"NAME" = \'Barnes\' AND "STATEFP" = \'38\'')
arcpy.Select_analysis("uscounty","RansomCounty.shp",'"NAME" = \'Ransom\' AND "STATEFP" = \'38\'')
arcpy.Select_analysis("ND_roads","ND_PrimaryRoads.shp",'"MTFCC" = \'S1100\'')


#----Part 2---- Lists and Loops-----#
#Creating List of the Counties and Features used for different analysis and algorthims
#Counties List is used to double loop
#Features are the list of all the possible features in the gdb
#BufferFeatures are features required to be buffered
#NetworkFeatures are used for NetworkAnalysis Service Areas and Finding the Closest Facility
Counties = ["CassCounty","TraillCounty","SteeleCounty","BarnesCounty","RansomCounty"]
Features = ["Ambupoints", "Cellular","ND_roads","Hospitals","ND_PrimaryRoads"]
BufferFeatures = ["Hospitals","Cellular","ND_PrimaryRoads"]
NetworkFeatures = ["Ambupoints","Hospitals","ND_roads"]
BufferedFeatures = ["Hospitalsbuffered","Cellularbuffered","ND_PrimaryRoadsbuffered"]



# 
#clippedFeatures = []
i = 0
for feat in Features:
	for county in Counties:
		arcpy.Clip_analysis(feat,county, county+feat+"clip"+str(i))
		i = i+1
#		clippedFeatures.append(item)

#Merge different counties together to analyze them as group in a network
arcpy.Merge_management(["CassCounty","TraillCounty","SteeleCounty","BarnesCounty","RansomCounty"],"ND_Counties")


#Clip all the netfeatures to the new merged counties layer created 
for netfeat in NetworkFeatures:
	arcpy.Clip_analysis(netfeat,"ND_Counties", netfeat+"ND_Counties")

#Buffer all the bufffeat 
for bufffeat in BufferFeatures:
		arcpy.Buffer_analysis(bufffeat,bufffeat+"buffered","1 MILE","FULL","ROUND", "ALL")

#Clip the buffered features to the Merged Counties layer 
# Can also be edited to clip for indiviudal counties also 
for buffered in BufferedFeatures:
        arcpy.Clip_analysis(buffered,"ND_counties",buffered+"ND_Counties")


#----Part 3---- Network Analyst-----#


#had to create network intially from CassCountRoads from Wizard Cannot do it in arcpy or python

#Build a Network for Service Areas and For CLosest Facility Layer
arcpy.na.BuildNetwork("ND_CountyRoads_Network")
#Create  A Service Area using the ND-County_Roads Network, 
#Used Length and 2000 Meter intervals. (5 Mile Radius Roughly)
#adding locations which are The Ambulance Dispatch Points and then solving the Network. 

arcpy.na.MakeServiceAreaLayer("ND_CountyRoads_Network","AmbulanceServiceAreas","Length","","2000 4000 6000 8000")
arcpy.na.AddLocations("AmbulanceServiceAreas","Facilities","AmbuPointsclip")
arcpy.na.Solve("AmbulanceServiceAreas")

#Create a Closet Facility layer, using Length and using Hospital as the Faicilites to travel 
#The Incidents were the Ambulance Dispatch points where they will travel from.
#Finally Solved Closest Facility Layer

arcpy.na.MakeClosestFacilityLayer("ND_CountyRoads_Network","ClosestAmbulance","Length","TRAVEL_TO")
arcpy.na.AddLocations("ClosestAmbulance","Facilities","HospitalsND_Counties")
arcpy.na.AddLocations("ClosestAmbulance","Incidents","AmbupointsND_Counties")
arcpy.na.Solve("ClosestAmbulance")



