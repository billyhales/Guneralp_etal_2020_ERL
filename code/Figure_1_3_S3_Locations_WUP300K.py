#!python3

#This script was used to produce plots for Figures 1, 3, and S3 of
#Guneralp B, M Reba, BU Hales, EA Wentz, & KC Seto (2020)
#Trends in Urban land expansion, density, and land transitions from 1970 to 2010: a global synthesis
#Environmental Research Letters, 15(4): 044015
##
#Author: Billy Hales
#Made: 8 December 2019
#Environment: Python 3.8 for Windows 10
#Software Used:
##  Python 3.8 with the following modules:
##      NumPy, 1.19.1
##      Matplotlib, 3.3.0
##      Pandas, 1.1.0
#Revisions: 3
#Date of Last Revision: 18 August 2020
#History of Revisions:
##  1. Adapted to work with simplified input file.
##  2. Optimized code to make more readable.
##  3. Adapted to record bootstrapped points in set of output files.
#Execution Details: This script is executed on the command line.
##  Example commandline:
##      .\Figure_1_3_S3_Locations_WUP300K.py Input_ranked-by-LocationName_WUP300K.csv
##  This script is OS-Dependent, as it calls the 'chcp' command to both fetch the current 
##      codepage and change to the UTF-8 codepage to make unicode entries within the inpute script
##      readable.
##  This script requires a working LaTeX installation for formatting on the labels. The LaTeX used
##      is a software called MikTeX,
##      URL: http://miktex.org
#Inputs:
##  Input File (CSV)
##      This input file is expected to be in comma-separated values format, and have a particular
##      order of data columns. These are currently:
##          1. Urban Agglomeration Name
##          2. Country
##          3. Region
##          4. OID
##          5-9. Population for 1970,1980,1990,2000,2010 (1000's of people)
##          10-13. Rate of Population Change for 1970-1980,1980-1990,1990-2000,2000-2010 (%)
##          14-18. Estimated Urban area for 1970,1980,1990,2000,2010 (km^2)
##          19-22. Rate of Urban Area Expansion for 1970-1980,1980-1990,1990-2000,2000-2010 (%)
##          23-27. Estimated Population Density for 1970,1980,1990,2000,2010 (people/km2)
#Outputs:
##  This script outputs three sets of outputs.
##      1. 12 Output images that present the data with three categories:
##          1. linear and logarithmic axes
##          2. rates of urban expansion vs. rates of population change and population density
##          3. three population size classes (all, above 2 million, and below 2 million)
##      2. 1 summary file that prints out means and medians of regions for all plots.
##      3. 1 Output xlsx file with 6 sheets, where each sheet presents bootstrapped estimates of location-averaged values in two categories:
##          1. rates of urban expansion vs. rates of population change and population density
##          2. three population size classes (all, above 2 million, and below 2 million)

##Imported Modules
import os, sys, numpy, math, copy, warnings, subprocess, pandas
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as tker
from matplotlib.ticker import FormatStrFormatter
from builtins import str

#LaTeX related formatting boilerplate
matplotlib.use('TkAgg')
matplotlib.rcParams['text.usetex'] = True
##Label formatting boilerplate
matplotlib.rc('font',**{'family':'sans-serif','sans-serif':['Arial']})
matplotlib.rc('xtick', labelsize=7)
matplotlib.rc('ytick', labelsize=7)

#Code to enable UTF-8 UNICODE in Windows/DOS. 
##We have to change a bytes object from STDOUT to a string object.
p = subprocess.Popen(['chcp'],shell=True,stdout=subprocess.PIPE)
msg = "".join([chr(x) for x in p.stdout.readline().split(b" ")[-1].strip()])
##Code to enable UTF-8 UNICODE in Windows/DOS
subprocess.Popen(['chcp','65001'],shell=True,stdout=subprocess.PIPE)

#Code to create estimates that are bootstrapped by means with replacement.
#Inputs:
##  bs_iter - Number of desired estimates in bootstrap. (Currently 1000).
##  *data - data sets of urban expansion rate in decade-Intervals (4) or population density in decades (5) where we compute bootstraps from the samples
#Outputs:
##  This function computes bootstrapped estimates for each decade-interval or decade for a region.
def bstrap(bs_iter,*data):
    #If there are four decades, then assume rates of change and allocate four decades.
    if len(list(data)) == 4:
        opt = "rate"
        data70,data80,data90,data00 = data
    #If there are five decades, then assume PD and allocate five decades.
    elif len(list(data)) == 5:
        opt = "PD"
        data70,data80,data90,data00,data10 = data
    #If neither, raise an error.
    else:
        raise Exception("Number of Decades should be 4 or 5")
    #If rates of change, do not divide by 1000.
    if opt == "rate":
        numr8tr = 1
    #If PD, then divide by 1000 to display on charts
    else:
        numr8tr = 1000

    #If there are any measurements for a given region in the year 1970...
    if len(data70) > 0:
        data70 = [float(x)/numr8tr for x in data70]
        npy70 = numpy.array(data70)
        #Bootstrap Procedure:
        #The following steps are done 1000 times for a group of size N:
        #    The following steps are done N times:
        #        In each group of size N, a random member from that group is drawn.
        #    With a collection of N randomly drawn members, calculate the mean.
        #    Add the mean to the bootstrap result
        bs70 = numpy.mean(numpy.random.choice(npy70,size=(bs_iter,npy70.shape[0]),replace=True),axis=1)
    #Otherwise just output an empty array.
    else:
        bs70 = numpy.array([])
    if len(data80) > 0:                
        data80 = [float(x)/numr8tr for x in data80]
        npy80 = numpy.array(data80)
        bs80 = numpy.mean(numpy.random.choice(npy80,size=(bs_iter,npy80.shape[0]),replace=True),axis=1)
    else:
        bs80 = numpy.array([])
    if len(data90) > 0:
        data90 = [float(x)/numr8tr for x in data90]
        npy90 = numpy.array(data90)
        bs90 = numpy.mean(numpy.random.choice(npy90,size=(bs_iter,npy90.shape[0]),replace=True),axis=1)
    else:
        bs90 = numpy.array([])
    if len(data00) > 0:
        data00 = [float(x)/numr8tr for x in data00]
        npy00 = numpy.array(data00)
        bs00 = numpy.mean(numpy.random.choice(npy00,size=(bs_iter,npy00.shape[0]),replace=True),axis=1)
    else:
        bs00 = numpy.array([])
    #If there are five decades, then do a bootstrap of PD for 2010.
    if opt != "rate":
        if len(data10) > 0:
            data10 = [float(x)/1000 for x in data10]
            npy10 = numpy.array(data10)
            bs10 = numpy.mean(numpy.random.choice(npy10,size=(bs_iter,npy10.shape[0]),replace=True),axis=1)
        else:
            bs10 = numpy.array([])

    #Return the appropriate number of decades.
    if opt == "rate":
        return bs70,bs80,bs90,bs00
    else:
        return bs70,bs80,bs90,bs00,bs10

#Code to calculate the mean of values of interest between studies that cover the same location
#and add the mean to a new sample of data. Measurements that have only one study at location are not affected.
#Inputs:
##  regions - List of regions, where eatch datum in a region is a data structure that has multiple attributes of the studies that comprise them.
##  m - Index of current region
##  data_index_start - This is the beginning column index.
##      Please keep in mind that Python is zero-indexed, which means that the 10th column corresponds to number 9.
##  data_index_end - This is the last column index + 1.
##      Since the value is +1, we return to natural counting, which means that the 10th column corresponds to number 10.
#Outputs:
##  a collection of values of averaged estimates for each decade (works with 4 decade intervals or 5 decades)
def loc_average(regions,m,data_index_start,data_index_end):
    #Get the names of all urban agglomerations.
    loc_name = list(zip(*regions[m]))[0]
    #Are we dealing with 4 decade-intervals or 5 decades? Look at interval between data_index_start and data_index_end
    #This sets up an appropriate data extraction and sets the opt token for other operations.
    #If the number of decades is not 4 or 5, then thrown an error.
    if data_index_end - data_index_start == 4:
        opt = "rate"
        data70,data80,data90,data00 = list(zip(*regions[m]))[data_index_start:data_index_end]
    elif data_index_end - data_index_start == 5:
        opt = "PD"
        data70,data80,data90,data00,data10 = list(zip(*regions[m]))[data_index_start:data_index_end]
    else:
        raise Exception("Number of decades should be 4 or 5.")

    #Create list of unique urban agglomeration names.
    loc_name_unique = []
    for i in range(len(loc_name)):
        if loc_name_unique.count(loc_name[i]) == 0:
            loc_name_unique.append(loc_name[i])
    #Set up lists for change that is averaged at each location
    if opt == "rate":
        loc70,loc80,loc90,loc00 = [],[],[],[]
    else:
        loc70,loc80,loc90,loc00,loc10 = [],[],[],[],[]
    #For Each Urban Agglomeration...
    for j in range(len(loc_name_unique)):
        #Create a list of indices that correspond to each urban agglomeration with a particular name.
        loc_index = []
        #Go through all urban agglomeration names to see which match the current urban agglomeration.
        for i in range(len(loc_name)):
            if loc_name[i] == loc_name_unique[j]:
                loc_index.append(i)
        #Sums all percent change that are attributed to a particular urban agglomeration
        if opt == "rate":
            sum_loc70,sum_loc80,sum_loc90,sum_loc00,sub_loc70,sub_loc80,sub_loc90,sub_loc00 = 0,0,0,0,0,0,0,0
        else:
            sum_loc70,sum_loc80,sum_loc90,sum_loc00,sum_loc10,sub_loc70,sub_loc80,sub_loc90,sub_loc00,sub_loc10 = 0,0,0,0,0,0,0,0,0,0
        for k in range(len(loc_index)):
            if data70[loc_index[k]] != '' and data70[loc_index[k]] != ' ':
                #If there is data, add study to sum for 70-80
                sum_loc70 += float(data70[loc_index[k]])
            else:
                #If no data, increase the amount to subtract from all studies that are of the specific Urban Agglomeration for 70-80
                sub_loc70 += 1 
            if data80[loc_index[k]] != '' and data80[loc_index[k]] != ' ':
                sum_loc80 += float(data80[loc_index[k]])
            else:
                sub_loc80 += 1 
            if data90[loc_index[k]] != '' and data90[loc_index[k]] != ' ':
                sum_loc90 += float(data90[loc_index[k]])
            else:
                sub_loc90 += 1 
            if data00[loc_index[k]] != '' and data00[loc_index[k]] != ' ':
                sum_loc00 += float(data00[loc_index[k]])
            else:
                sub_loc00 += 1
            if opt != "rate":
                if data10[loc_index[k]] != '' and data10[loc_index[k]] != ' ':
                    sum_loc10 += float(data10[loc_index[k]])
                else:
                    sub_loc10 += 1
                
        if (len(loc_index)-sub_loc70) > 0:
            #If there are values for 70-80, append location mean for loc70
            loc70.append(sum_loc70/(len(loc_index)-sub_loc70))
        if (len(loc_index)-sub_loc80) > 0:
            loc80.append(sum_loc80/(len(loc_index)-sub_loc80))
        if (len(loc_index)-sub_loc90) > 0:
            loc90.append(sum_loc90/(len(loc_index)-sub_loc90))
        if (len(loc_index)-sub_loc00) > 0:
            loc00.append(sum_loc00/(len(loc_index)-sub_loc00))
        if opt != "rate":
            #If there are five decades, take the mean of the last decade.
            if (len(loc_index)-sub_loc10) > 0:
                loc10.append(sum_loc10/(len(loc_index)-sub_loc10))

    #Return the appropriate number of decades.
    if opt == "rate":
        return loc70[:],loc80[:],loc90[:],loc00[:]
    else:
        return loc70[:],loc80[:],loc90[:],loc00[:],loc10[:]

#This function makes six linear-scaled plots that correspond to rates of urban expansion vs population change and
#population density for all three size classes (all, above 2 million, below 2 million). This function generates bootstrapped
#estimates that are then output (see Outputs) and input into the plot_log function.
##Inputs:
##  regions - For each region, composes of all the data in the input spread sheet.
##  region_unique - The list of region-keywords, in order that they will be displayed on the charts.
##  label_dict - A lexicon that relates region-keywords to labels that will appear on the charts.
##  ifile_path - The path of the input file. This tells the function where to put the plots.
##  summary_output_file_handle - This file contains outputs means and medians of the bootstrap estimates
##    for each region, population size class, and decade-interval or decade.
##  bstrap_output_file_handle - This file contains outputs of computed bootstrap estimates
##    for each region, population size class, and decade-interval or decade.
##  opic_string - This determins the format of the output file names.
##  number_of_decade_intervals - This is the number of decade-intervals (4). Decades are supposed to be decade-intervals + 1
##  ylimList - Y axis limits of each chart.
##Outputs:
##  bs_pack1 - This has the bootstrapped estimates for urban expansion rate for each size class, each decade-interval, and each region.
##  bs_pack2 - This has the bootstrapped estimates for population density for each size class, each decade, and each region.
##  region_means - This file has all the means and medians computed from bootstrapped estimates.
def plot_linear(regions,region_unique,label_dict,ifile_path,summary_output_file_handle,bstrap_output_file_handle,opic_string,number_of_decade_intervals,ylimList):
    region_means = []
    #For Each Region...
    for m in range(len(region_unique)):
        #Create estimates that are averaged from studies that cover the same location.
        pop_perc_1970,pop_perc_1980,pop_perc_1990,pop_perc_2000 = loc_average(regions,m,9,13)
        #Set up place to store means of all location-averaged population data.
        means = []
        try:
            means.append(sum(pop_perc_1970)/len(pop_perc_1970))
        except ZeroDivisionError:
            means.append(numpy.nan)
        try:
            means.append(sum(pop_perc_1980)/len(pop_perc_1980))
        except ZeroDivisionError:
            means.append(numpy.nan)
        try:
            means.append(sum(pop_perc_1990)/len(pop_perc_1990))
        except ZeroDivisionError:
            means.append(numpy.nan)
        try:
            means.append(sum(pop_perc_2000)/len(pop_perc_2000))
        except ZeroDivisionError:
            means.append(numpy.nan)
        region_means.append(means)

    #Set up plot
    ##  Set up figure dimensions for Urban Area Expansion Rate and Population Change Rate
    fig = plt.figure(1,figsize=(8,3))
    ##Set plot inside figure. This one is for population precentage.
    tp_axis = plt.axes([0.085,0.2,0.83,0.65])
    ##Clear X axis of default ticks.
    nullfmt = tker.NullFormatter()
    tp_axis.xaxis.set_major_formatter(nullfmt)

    #Set up offset for estimates for each decade.
    start = 1
    xtick_list = []
    ##Set up dash symbol to represent percent population change.
    verts = [(-0.1,-0.02),(-0.1,0.02),(0.1,0.02),(0.1,-0.02)]
    ##For each region...
    for item in region_means:
        ##Set up colors for decades 70-80,80-90,90-00,00-10
        colors = [(0.0,0.0,0.6,1.0),(0.6,0.0,0.0,1.0),(0.0,0.6,0.0,1.0),(0.6,0.6,0.0,1.0)]
        ##Plot the custom symbol for each decade.
        tp_axis.scatter(range(start,len(item)+start),item,s=50,marker=verts,color=colors,picker=True)
        ##Set up positions to annotate for reach region.
        xtick_list.append(start+((len(item))/2.0)-0.5)        
        start += number_of_decade_intervals + 1

    #Set up plot pt. 2
    ##Set min,max of x axis
    tp_axis.set_xlim(0,51)
    ##Set min,max of y axis
    tp_axis.set_ylim(ylimList[0][0],ylimList[0][1])

    #Sets the y axis with increments of 2 between low value and high value on left y axis.
    tp_yticks = []
    l = ylimList[0][0]
    while l <= ylimList[0][1]:
        tp_yticks.append(l)
        l+=2
    if tp_yticks[-1] != ylimList[0][1]:
        tp_yticks.append(ylimList[0][1])
    tp_axis.set_yticks(tp_yticks)

    #Set up some gridlines to correspond to each y tick, except the top and bottom of the plot.
    for xtick in tp_yticks[1:-1]:
        plt.plot([0,100],[xtick,xtick],linestyle=':',color=(0.8,0.8,0.8),linewidth=0.5,alpha=0.35)

    #Create an axis on the right side of the plot. This axis will cover urban expansion percentage.
    mi_axis = tp_axis.twinx()

    #Set up space to put ticks and tick lables for x axis.
    xtick_list,xtick_label_list = [],[]
    start = 1
    k = 1

    #Set up space for output to put bootstrapped urban expansion rates logarithmic plot.
    bs_pack1 = []
    bs_dict1 = {}
    #For each region...
    for m, cur_region in enumerate(region_unique):
        #Retrieve urban expansion estimates
        data70,data80,data90,data00 = loc_average(regions,m,18,22)

        #Create bootstrapped estimates of urban expansion estimates
        bs70,bs80,bs90,bs00 = bstrap(1000,data70,data80,data90,data00)

        #Prepare the output for use in logarithmic plots.
        bs_pack1.append((bs70,bs80,bs90,bs00))

        #Ignores a runtimewarning when mean is calculated for empty list.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            #Output means and medians of bootstrapped estimates to summary statistics file.
            bs70_mean,bs80_mean,bs90_mean,bs00_mean = numpy.mean(bs70.astype(numpy.float64)),numpy.mean(bs80.astype(numpy.float64)),numpy.mean(bs90.astype(numpy.float64)),numpy.mean(bs00.astype(numpy.float64))
            bs70_median,bs80_median,bs90_median,bs00_median = numpy.median(bs70.astype(numpy.float64)),numpy.median(bs80.astype(numpy.float64)),numpy.median(bs90.astype(numpy.float64)),numpy.median(bs00.astype(numpy.float64))
        summary_output_file_handle.write("{:s}\nUrban Expansion Rates\n{:s}\n1970 Mean,{:.15f}\n1970 Median,{:.15f}\n1980 Mean,{:.15f}\n1980 Median,{:.15f}\n1990 Mean,{:.15f}\n1990 Median,{:.15f}\n2000 Mean,{:.15f}\n2000 Median,{:.15f}\n".format(cur_region,opic_string,bs70_mean,bs70_median,bs80_mean,bs80_median,bs90_mean,bs90_median,bs00_mean,bs00_median))

        for bs_item in [('70-80',bs70),('80-90',bs80),('90-00',bs90),('00-10',bs00)]:
            bs_key = '_'.join([cur_region.replace(' ','_'),opic_string,bs_item[0]])
            bs_data = bs_dict1.get(bs_key,0)
            if len(bs_item[1]) == 0:
                continue
            if bs_data == 0:
                bs_dict1[bs_key] = bs_item[1].tolist()

        #Create data_array to inputation into the plot. orig_array is used to calculate number of estimates.
        data_array = [bs70,bs80,bs90,bs00]
        orig_array = [data70,data80,data90,data00]
        #Sets up attributes for setting properties of boxplot.
        color_array = [(0.0,0.0,0.6,0.3),(0.6,0.0,0.0,0.3),(0.0,0.6,0.0,0.3),(0.6,0.6,0.0,0.3)]
        index_array = [(0,1,1,1,0,1,0,1,0),(1,3,3,3,2,3,2,3,1),(2,5,5,5,4,5,4,5,2),(3,7,7,7,6,7,6,7,3)]

        #Sets up crude boxplot.
        bp = mi_axis.boxplot(data_array,positions=list(numpy.linspace(start,4+start,4,False)),patch_artist=True,showfliers=False,zorder=10)

        #Sets up jitter part of box-jitter plots and other cosmetic features.
        scatter_list = []
        for j in range(4):
            plt.setp(bp['boxes'][index_array[j][0]],    color=(0.6,0.6,0.6), lw=0.25, fill=False)
            yanno = plt.getp(bp['caps'][index_array[j][1]],'ydata')[0]
            xanno = (plt.getp(bp['caps'][index_array[j][2]],'xdata')[0]+plt.getp(bp['caps'][index_array[j][3]],'xdata')[1])/2.0
            #Ensures that width of jitter on bow jitter plot does not exceed width of boxplot element.
            jitter_bias = abs(plt.getp(bp['caps'][index_array[j][2]],'xdata')[0]-xanno)
            jitter = numpy.add(numpy.multiply(numpy.random.random_sample(len(data_array[j])),(2.0*jitter_bias)),(xanno-jitter_bias))
            #This makes jitter plot and records handle for legend.
            scatter_list.append(plt.scatter(jitter, data_array[j], c=[color_array[j]], marker='o', edgecolors='none', alpha=0.1, s=0.2, zorder=5))
            #This sets up numbers on top of boxplots
            plt.annotate('{:d}'.format(len(orig_array[j])),xy=(xanno,yanno),xytext=(0,2),size=5.25,horizontalalignment='center',textcoords='offset points')
            #Makes edges of boxplots for less thickness and grey color.
            plt.setp(bp['caps'][index_array[j][4]], color=(0.6,0.6,0.6), lw=0.25)
            plt.setp(bp['caps'][index_array[j][5]], color=(0.6,0.6,0.6), lw=0.25)
            plt.setp(bp['whiskers'][index_array[j][6]], color=(0.6,0.6,0.6), lw=0.25)
            plt.setp(bp['whiskers'][index_array[j][7]], color=(0.6,0.6,0.6), lw=0.25)
            plt.setp(bp['medians'][index_array[j][8]], color=(0.6,0.6,0.6), lw=0.25)
        #Sets up ticks to annotate different regions.
        xtick_list.append(start+((4)/2.0)-0.5)
        start += number_of_decade_intervals + 1

    df = pandas.DataFrame(bs_dict1)
    df.to_excel(bstrap_output_file_handle, sheet_name="UER_{:s}".format(opic_string))

    #This sets the x and y limits.
    mi_axis.set_xlim(0,51)
    mi_axis.set_ylim(ylimList[0][0],ylimList[0][1])
    
    #Sets the y axis with increments of 2 between low value and high value on right y axis.
    tp_yticks = []
    l = ylimList[0][0]
    while l <= ylimList[0][1]:
        tp_yticks.append(l)
        l+=2
    if tp_yticks[-1] != ylimList[0][1]:
        tp_yticks.append(ylimList[0][1])
    mi_axis.set_yticks(tp_yticks)

    #Sets annotation for x axis.
    tp_axis.set_xticks(xtick_list)
    tp_axis.set_xticklabels([label_dict[x] for x in region_unique],horizontalalignment='right',rotation=30,family='sans-serif')
    tp_axis.yaxis.set_major_formatter(FormatStrFormatter('%d'))

    #Sets label for right y axes.
    tp_axis.set_ylabel("$$\mathrm{percent\hspace{2pt}change:\hspace{2pt}population}$$",family='sans-serif')
    mi_axis.set_ylabel("$$\mathrm{percent\hspace{2pt}change:\hspace{2pt}urban\hspace{2pt}area}$$",rotation=270,verticalalignment='bottom',family='sans-serif')
    mi_axis.yaxis.set_major_formatter(FormatStrFormatter('%d'))

    #Sets up legend for plot
    leg = tp_axis.legend(tuple(scatter_list),("1970-1980","1980-1990","1990-2000","2000-2010"),scatterpoints=1,markerscale=10.0,edgecolor=(0,0,0),fontsize=6.0,loc="upper left",bbox_to_anchor=(0.02,0.98))
    for lh in leg.legendHandles:
        lh.set_alpha(1)
    leg.set_zorder(20)
    leg.set_alpha(1)

    #Save plot as PNG image.
    fig.savefig(os.path.join(os.path.split(ifile_path)[0],'{:s}_rates_linear.png'.format(opic_string)),dpi=300)
    #Show plot.
    plt.show()
    
    #Set up figure dimensions for Population Density
    fig = plt.figure(2,figsize=(8,3))
    bt_axis = plt.axes([0.085,0.2,0.82,0.65])

    xtick_list = []
    xtick_label_list = []
    start = 1
    k = 1

    #Set up space for output to put bootstrapped population density logarithmic plot.
    bs_pack2 = []
    bs_dict2 = {}
    #For each region...
    for m, cur_region in enumerate(region_unique):
        #Create estimates that are averaged from studies that cover the same location.
        data70,data80,data90,data00,data10 = loc_average(regions,m,22,27)

        #Create bootstrapped estimates of urban expansion estimates
        bs70,bs80,bs90,bs00,bs10 = bstrap(1000,data70,data80,data90,data00,data10)

        #Prepare the output for use in logarithmic plots.
        bs_pack2.append((bs70,bs80,bs90,bs00,bs10))

        #Ignores a runtimewarning when mean is calculated for empty list.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            #Output means and medians of bootstrapped estimates to summary statistics file.
            bs70_mean,bs80_mean,bs90_mean,bs00_mean,bs10_mean = numpy.mean(bs70.astype(numpy.float64)),numpy.mean(bs80.astype(numpy.float64)),numpy.mean(bs90.astype(numpy.float64)),numpy.mean(bs00.astype(numpy.float64)),numpy.mean(bs10.astype(numpy.float64))
            bs70_median,bs80_median,bs90_median,bs00_median,bs10_median = numpy.median(bs70.astype(numpy.float64)),numpy.median(bs80.astype(numpy.float64)),numpy.median(bs90.astype(numpy.float64)),numpy.median(bs00.astype(numpy.float64)),numpy.median(bs10.astype(numpy.float64))
        summary_output_file_handle.write("{:s}\nPopulation Density\n{:s}\n1970 Mean,{:.15f}\n1970 Median,{:.15f}\n1980 Mean,{:.15f}\n1980 Median,{:.15f}\n1990 Mean,{:.15f}\n1990 Median,{:.15f}\n2000 Mean,{:.15f}\n2000 Median,{:.15f}\n2010 Mean,{:.15f}\n2010 Median,{:.15f}\n".format(cur_region,opic_string,bs70_mean,bs70_median,bs80_mean,bs80_median,bs90_mean,bs90_median,bs00_mean,bs00_median,bs10_mean,bs10_median))

        for bs_item in [('1970',bs70),('1980',bs80),('1990',bs90),('2000',bs00),('2010',bs10)]:
            bs_key = '_'.join([cur_region.replace(' ','_'),opic_string,bs_item[0]])
            bs_data = bs_dict2.get(bs_key,0)
            if len(bs_item[1]) == 0:
                continue
            if bs_data == 0:
                bs_dict2[bs_key] = bs_item[1].tolist()

        #Create data_array to inputation into the plot. orig_array is used to calculate number of estimates.
        data_array = [bs70,bs80,bs90,bs00,bs10]
        orig_array = [data70,data80,data90,data00,data10]
        #Sets up attributes for setting properties of boxplot.
        color_array = [(0.0,0.0,0.6,0.3),(0.6,0.0,0.0,0.3),(0.0,0.6,0.0,0.3),(0.6,0.6,0.0,0.3),(0.6,0.6,0.6,0.3)]
        index_array = [(0,1,1,1,0,1,0,1,0),(1,3,3,3,2,3,2,3,1),(2,5,5,5,4,5,4,5,2),(3,7,7,7,6,7,6,7,3),(4,9,9,9,8,9,8,9,4)]

        #Sets up crude boxplot.
        bp = plt.boxplot(data_array,positions=list(numpy.linspace(start,5+start,5,False)),patch_artist=True,showfliers=False,zorder=10)

        #Sets up jitter part of box-jitter plots and other cosmetic features.
        scatter_list = []
        for j in range(5):
            plt.setp(bp['boxes'][index_array[j][0]], color=(0.6,0.6,0.6), lw=0.25, fill=False)
            yanno = plt.getp(bp['caps'][index_array[j][1]],'ydata')[0]
            xanno = (plt.getp(bp['caps'][index_array[j][2]],'xdata')[0]+plt.getp(bp['caps'][index_array[j][3]],'xdata')[1])/2.0
            #Ensures that width of jitter on bow jitter plot does not exceed width of boxplot element.
            jitter_bias = abs(plt.getp(bp['caps'][index_array[j][2]],'xdata')[0]-xanno)
            jitter = numpy.add(numpy.multiply(numpy.random.random_sample(len(data_array[j])),(2.0*jitter_bias)),(xanno-jitter_bias))
            #This makes jitter plot and records handle for legend.
            scatter_list.append(plt.scatter(jitter, data_array[j], c=[color_array[j]], marker='o', edgecolors='none', alpha=0.1, s=0.2, zorder=5))
            #This sets up numbers on top of boxplots
            plt.annotate('{:d}'.format(len(orig_array[j])),xy=(xanno,yanno),xytext=(0,2),size=5.25,horizontalalignment='center',textcoords='offset points')
            #Makes edges of boxplots for less thickness and grey color.
            plt.setp(bp['caps'][index_array[j][4]],     color=(0.6,0.6,0.6), lw=0.25)
            plt.setp(bp['caps'][index_array[j][5]],     color=(0.6,0.6,0.6), lw=0.25)
            plt.setp(bp['whiskers'][index_array[j][6]], color=(0.6,0.6,0.6), lw=0.25)
            plt.setp(bp['whiskers'][index_array[j][7]], color=(0.6,0.6,0.6), lw=0.25)
            plt.setp(bp['medians'][index_array[j][8]],  color=(0.6,0.6,0.6), lw=0.25)

        #Sets up legend for plot
        leg = bt_axis.legend(tuple(scatter_list),("1970","1980","1990","2000","2010"),scatterpoints=1,markerscale=10.0,edgecolor=(0,0,0),fontsize=6.0,loc="upper left",bbox_to_anchor=(0.02,0.98))
        for lh in leg.legendHandles:
            lh.set_alpha(1)
        leg.set_zorder(20)
        leg.set_alpha(1)
        xtick_list.append(start+((5)/2.0)-0.5)
        start += number_of_decade_intervals + 2

    df = pandas.DataFrame(bs_dict2)
    df.to_excel(bstrap_output_file_handle, sheet_name="PD_{:s}".format(opic_string))

    #Sets annotation for y axis.
    bt_axis.set_ylim(ylimList[1][0],ylimList[1][1])
    bt_yticks = []
    bt_yticks.append(ylimList[1][0])
    for l in range(10,ylimList[1][1],10):
        if l != ylimList[1][0]:
            bt_yticks.append(l)
    if bt_yticks[-1] != ylimList[1][1]:
        bt_yticks.append(ylimList[1][1])
    bt_axis.set_yticks(bt_yticks)

    #Set up some gridlines to correspond to each y tick, except the top and bottom of the plot.
    for xtick in bt_yticks[1:-1]:
        plt.plot([0,100],[xtick,xtick],linestyle=':',color=(0.8,0.8,0.8),linewidth=0.5,alpha=0.35)

    #Sets annotation for x axis.    
    bt_axis.set_xlim(0,60)
    bt_axis.set_xticks(xtick_list)
    bt_axis.set_xticklabels([label_dict[x] for x in region_unique],rotation=30,ha='right',family='sans-serif')

    #Sets up annotation for right y axis.
    bt_twin = bt_axis.twinx()
    bt_twin.set_ylim(ylimList[1][0],ylimList[1][1])
    bt_yticks = []
    bt_yticks.append(ylimList[1][0])
    for l in range(10,ylimList[1][1],10):
        if l != ylimList[1][0]:
            bt_yticks.append(l)
    if bt_yticks[-1] != ylimList[1][1]:
        bt_yticks.append(ylimList[1][1])
    bt_twin.set_yticks(bt_yticks)

    #Set formatting for y axes
    bt_axis.yaxis.set_major_formatter(FormatStrFormatter('%d'))
    bt_twin.yaxis.set_major_formatter(FormatStrFormatter('%d'))

    #Set lables for y axes
    bt_axis.set_ylabel("$$\mathrm{10^3\hspace{2pt}people\hspace{2pt}per\hspace{2pt}km^2}$$",family='sans-serif')
    bt_twin.set_ylabel("$$\mathrm{10^3\hspace{2pt}people\hspace{2pt}per\hspace{2pt}km^2}$$",rotation=270,verticalalignment='bottom',family='sans-serif')

    #Save plot as PNG image.
    fig.savefig(os.path.join(os.path.split(ifile_path)[0],'{:s}_PD_linear.png'.format(opic_string)),dpi=300)
    #Show plot
    plt.show()
    return bs_pack1,bs_pack2,region_means

#This function makes six log-scaled plots that correspond to rates of urban expansion vs population change and
#population density for all three size classes (all, above 2 million, below 2 million). This function generates bootstrapped
#estimates that are then output (see Outputs) and input into the plot_log function.
##Inputs:
##  regions - For each region, composes of all the data in the input spread sheet.
##  region_unique - The list of region-keywords, in order that they will be displayed on the charts.
##  label_dict - A lexicon that relates region-keywords to labels that will appear on the charts.
##  ifile_path - The path of the input file. This tells the function where to put the plots.
##  opic_string - This determins the format of the output file names.
##  number_of_decade_intervals - This is the number of decade-intervals (4). Decades are supposed to be decade-intervals + 1
##  ylimList - Y axis limits of each chart.
##  bs_pack1 - This has the bootstrapped estimates for urban expansion rate taken from plot_linear function.
##  bs_pack2 - This has the bootstrapped estimates for population density taken from plot_linear function.
##  region_means - This file has all the means and medians computed from bootstrapped estimates, and taken from plot_linear function..
##Outputs:
##  bs_pack1 - This has the bootstrapped estimates for urban expansion rate for each size class, each decade-interval, and each region.
##  bs_pack2 - This has the bootstrapped estimates for population density for each size class, each decade, and each region.
##  region_means - This file has all the means and medians computed from bootstrapped estimates.
def plot_log(regions,region_unique,label_dict,ifile_path,opic_string,number_of_decade_intervals,ylimList,bs_pack1,bs_pack2,region_means):
    #Set up plot
    ##  Set up figure dimensions for Urban Area Expansion Rate and Population Change Rate
    fig = plt.figure(1,figsize=(8,3))
    ##Set plot inside figure. This one is for population precentage.
    tp_axis = plt.axes([0.085,0.2,0.83,0.65])
    ##Clear X axis of default ticks.
    nullfmt = tker.NullFormatter()
    tp_axis.xaxis.set_major_formatter(nullfmt)

    #Set up offset for estimates for each decade.
    start = 1
    xtick_list = []
    ##Set up dash symbol to represent percent population change.
    verts = [(-0.1,-0.02),(-0.1,0.02),(0.1,0.02),(0.1,-0.02)]
    ##For each region...
    tp_axis.set_yscale("log")
    for item in region_means:
        ##Set up colors for decades 70-80,80-90,90-00,00-10
        colors = [(0.0,0.0,0.6,1.0),(0.6,0.0,0.0,1.0),(0.0,0.6,0.0,1.0),(0.6,0.6,0.0,1.0)]
        ##Plot the custom symbol for each decade.
        tp_axis.scatter(range(start,len(item)+start),item,s=50,marker=verts,color=colors,picker=True)
        ##Set up positions to annotate for reach region.
        xtick_list.append(start+((len(item))/2.0)-0.5)
        start += number_of_decade_intervals + 1

    #Set up plot pt. 2
    ##Set min,max of x axis
    tp_axis.set_xlim(0,51)
    ##Set min,max of y axis
    tp_axis.set_ylim(ylimList[0][0],ylimList[0][1])

    #Sets the y axis by a power of 2 between low value and high value on left y axis.
    tp_yticks = []
    tp_yticks.append(ylimList[0][0])
    l = pow(2,0)
    n = 0
    while l <= ylimList[0][1]:
        if l != ylimList[0][0]:
            tp_yticks.append(l)
        n+=1
        l = pow(2,n)
    if tp_yticks[-1] != ylimList[0][1]:
        tp_yticks.append(ylimList[0][1])
    tp_axis.set_yticks(tp_yticks)

    #Clear ticks on y axis to account for software issue of overlapping axes.
    tp_axis.yaxis.set_minor_formatter(nullfmt)

    #Set up some gridlines to correspond to each y tick, except the top and bottom of the plot.
    for xtick in tp_yticks[1:-1]:
        plt.plot([0,100],[xtick,xtick],linestyle=':',color=(0.8,0.8,0.8),linewidth=0.5,alpha=0.35)

    #Create an axis on the right side of the plot. This axis will cover urban expansion percentage.
    mi_axis = tp_axis.twinx()

    #Set up space to put ticks and tick lables for x axis.
    xtick_list,xtick_label_list = [],[]
    start = 1
    k = 1
    #For each region...
    for m, cur_region in enumerate(region_unique):
        #Recieve values from linear plot
        bs70,bs80,bs90,bs00 = bs_pack1[m]

        #Create bootstrapped estimates of urban expansion estimates
        data70,data80,data90,data00 = loc_average(regions,m,18,22)

        #Create data_array to inputation into the plot. orig_array is used to calculate number of estimates.
        data_array = [bs70,bs80,bs90,bs00]
        orig_array = [data70,data80,data90,data00]
        #Sets up attributes for setting properties of boxplot.
        color_array = [(0.0,0.0,0.6,0.3),(0.6,0.0,0.0,0.3),(0.0,0.6,0.0,0.3),(0.6,0.6,0.0,0.3)]
        index_array = [(0,1,1,1,0,1,0,1,0),(1,3,3,3,2,3,2,3,1),(2,5,5,5,4,5,4,5,2),(3,7,7,7,6,7,6,7,3)]

        #Sets up crude boxplot.
        bp = mi_axis.boxplot(data_array,positions=list(numpy.linspace(start,4+start,4,False)),patch_artist=True,showfliers=False,zorder=10)


        #Sets up jitter part of box-jitter plots and other cosmetic features.
        scatter_list = []
        #For each decade interval...
        for j in range(4):
            plt.setp(bp['boxes'][index_array[j][0]], color=(0.6,0.6,0.6), lw=0.25, fill=False)
            yanno = plt.getp(bp['caps'][index_array[j][1]],'ydata')[0]
            xanno = (plt.getp(bp['caps'][index_array[j][2]],'xdata')[0]+plt.getp(bp['caps'][index_array[j][3]],'xdata')[1])/2.0
            #Ensures that width of jitter on bow jitter plot does not exceed width of boxplot element.
            jitter_bias = abs(plt.getp(bp['caps'][index_array[j][2]],'xdata')[0]-xanno)
            jitter = numpy.add(numpy.multiply(numpy.random.random_sample(len(data_array[j])),(2.0*jitter_bias)),(xanno-jitter_bias))
            #This makes jitter plot and records handle for legend.
            scatter_list.append(plt.scatter(jitter, data_array[j], c=[color_array[j]], marker='o', edgecolors='none', alpha=0.1, s=0.2, zorder=5))
            #This sets up numbers on top of boxplots
            plt.annotate('{:d}'.format(len(orig_array[j])),xy=(xanno,yanno),xytext=(0,2),size=5.25,horizontalalignment='center',textcoords='offset points')
            #Makes edges of boxplots for less thickness and grey color.
            plt.setp(bp['caps'][index_array[j][4]], color=(0.6,0.6,0.6), lw=0.25)
            plt.setp(bp['caps'][index_array[j][5]], color=(0.6,0.6,0.6), lw=0.25)
            plt.setp(bp['whiskers'][index_array[j][6]], color=(0.6,0.6,0.6), lw=0.25)
            plt.setp(bp['whiskers'][index_array[j][7]], color=(0.6,0.6,0.6), lw=0.25)
            plt.setp(bp['medians'][index_array[j][8]], color=(0.6,0.6,0.6), lw=0.25)
        #Sets up ticks to annotate different regions.
        xtick_list.append(start+((4)/2.0)-0.5)
        start += number_of_decade_intervals + 1

    #Set up axis as logarithmic
    mi_axis.set_yscale("log")
    #This sets the x and y limits.
    mi_axis.set_xlim(0,51)
    mi_axis.set_ylim(ylimList[0][0],ylimList[0][1])

    #Sets the y axis with increments of 2 between low value and high value on right y axis.
    tp_yticks = []
    tp_yticks.append(ylimList[0][0])
    l = pow(2,0)
    n = 0
    while l <= ylimList[0][1]:
        if l != ylimList[0][0]:
            tp_yticks.append(l)
        n+=1
        l = pow(2,n)
    if tp_yticks[-1] != ylimList[0][1]:
        tp_yticks.append(ylimList[0][1])
    mi_axis.set_yticks(tp_yticks)

    #Clear ticks on right y axis to account for software issue of overlapping axes.
    mi_axis.yaxis.set_minor_formatter(nullfmt)

    #Sets annotation for x axis.
    tp_axis.set_xticks(xtick_list)
    tp_axis.set_xticklabels([label_dict[x] for x in region_unique],horizontalalignment='right',rotation=30,family='sans-serif')
    tp_axis.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))

    #Sets label for right y axes.
    tp_axis.set_ylabel("$$\mathrm{percent\hspace{2pt}change:\hspace{2pt}population}$$",family='sans-serif')
    mi_axis.set_ylabel("$$\mathrm{percent\hspace{2pt}change:\hspace{2pt}urban\hspace{2pt}area}$$",rotation=270,verticalalignment='bottom',family='sans-serif')
    mi_axis.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))

    #Sets up legend for plot
    leg = tp_axis.legend(tuple(scatter_list),("1970-1980","1980-1990","1990-2000","2000-2010"),scatterpoints=1,markerscale=10.0,edgecolor=(0,0,0),fontsize=6.0,loc="lower left",bbox_to_anchor=(0.02,0.02))
    for lh in leg.legendHandles:
        lh.set_alpha(1)
    leg.set_zorder(20)
    leg.set_alpha(1)

    #Save plot as PNG image.
    fig.savefig(os.path.join(os.path.split(ifile_path)[0],'{:s}_rates_log.png'.format(opic_string)),dpi=300)
    #Show plot.
    plt.show()

    #Set up figure dimensions for Population Density
    fig = plt.figure(2,figsize=(8,3))
    bt_axis = plt.axes([0.085,0.2,0.82,0.65])

    xtick_list = []
    xtick_label_list = []
    start = 1
    k = 1
    
    #For each region...
    for m, cur_region in enumerate(region_unique):
        #Recieved values from linear plot
        bs70,bs80,bs90,bs00,bs10 = bs_pack2[m]
        #Create estimates that are averaged from studies that cover the same location.
        data70,data80,data90,data00,data10 = loc_average(regions,m,22,27)

        #Create data_array to inputation into the plot. orig_array is used to calculate number of estimates.
        data_array = [bs70,bs80,bs90,bs00,bs10]
        orig_array = [data70,data80,data90,data00,data10]
        #Sets up attributes for setting properties of boxplot.
        color_array = [(0.0,0.0,0.6,0.3),(0.6,0.0,0.0,0.3),(0.0,0.6,0.0,0.3),(0.6,0.6,0.0,0.3),(0.6,0.6,0.6,0.3)]
        index_array = [(0,1,1,1,0,1,0,1,0),(1,3,3,3,2,3,2,3,1),(2,5,5,5,4,5,4,5,2),(3,7,7,7,6,7,6,7,3),(4,9,9,9,8,9,8,9,4)]

        #Sets up crude boxplot.
        bp = plt.boxplot(data_array,positions=list(numpy.linspace(start,5+start,5,False)),patch_artist=True,showfliers=False,zorder=10)

        #Sets up jitter part of box-jitter plots and other cosmetic features.
        scatter_list = []
        #For each decade...        
        for j in range(5):
            plt.setp(bp['boxes'][index_array[j][0]],    color=(0.6,0.6,0.6), lw=0.25, fill=False)
            yanno = plt.getp(bp['caps'][index_array[j][1]],'ydata')[0]
            xanno = (plt.getp(bp['caps'][index_array[j][2]],'xdata')[0]+plt.getp(bp['caps'][index_array[j][3]],'xdata')[1])/2.0
            #Ensures that width of jitter on bow jitter plot does not exceed width of boxplot element.
            jitter_bias = abs(plt.getp(bp['caps'][index_array[j][2]],'xdata')[0]-xanno)
            jitter = numpy.add(numpy.multiply(numpy.random.random_sample(len(data_array[j])),(2.0*jitter_bias)),(xanno-jitter_bias))
            #This makes jitter plot and records handle for legend.
            scatter_list.append(plt.scatter(jitter, data_array[j], c=[color_array[j]], marker='o', edgecolors='none', alpha=0.1, s=0.2, zorder=5))
            #This sets up numbers on top of boxplots
            plt.annotate('{:d}'.format(len(orig_array[j])),xy=(xanno,yanno),xytext=(0,2),size=5.25,horizontalalignment='center',textcoords='offset points')
            #Makes edges of boxplots for less thickness and grey color.
            plt.setp(bp['caps'][index_array[j][4]],     color=(0.6,0.6,0.6), lw=0.25)
            plt.setp(bp['caps'][index_array[j][5]],     color=(0.6,0.6,0.6), lw=0.25)
            plt.setp(bp['whiskers'][index_array[j][6]], color=(0.6,0.6,0.6), lw=0.25)
            plt.setp(bp['whiskers'][index_array[j][7]], color=(0.6,0.6,0.6), lw=0.25)
            plt.setp(bp['medians'][index_array[j][8]],  color=(0.6,0.6,0.6), lw=0.25)

        #Sets up legend for plot
        leg = bt_axis.legend(tuple(scatter_list),("1970","1980","1990","2000","2010"),scatterpoints=1,markerscale=10.0,edgecolor=(0,0,0),fontsize=6.0,loc="upper left",bbox_to_anchor=(0.02,0.98))
        for lh in leg.legendHandles:
            lh.set_alpha(1)
        leg.set_zorder(20)
        leg.set_alpha(1)
        xtick_list.append(start+((5)/2.0)-0.5)
        start += number_of_decade_intervals + 2

    #Sets y axis as logarithmic
    bt_axis.set_yscale("log")

    #Sets annotation for y axis.
    bt_axis.set_ylim(ylimList[1][0],ylimList[1][1])
    bt_yticks = []
    bt_yticks.append(ylimList[1][0])
    for l in range(10,ylimList[1][1],10):
        if l != ylimList[1][0]:
            bt_yticks.append(l)
    if bt_yticks[-1] != ylimList[1][1]:
        bt_yticks.append(ylimList[1][1])
    bt_axis.set_yticks(bt_yticks)

    #Set grid for tick locations
    for xtick in bt_yticks[1:-1]:
        plt.plot([0,100],[xtick,xtick],linestyle=':',color=(0.8,0.8,0.8),linewidth=0.5,alpha=0.35)

    #Set annoatation for x axis
    bt_axis.set_xlim(0,60)
    bt_axis.set_xticks(xtick_list)
    bt_axis.set_xticklabels([label_dict[x] for x in region_unique],rotation=30,ha='right',family='sans-serif')

    #Clear ticks on right y axis to account for software issue of overlapping axes.
    bt_axis.yaxis.set_minor_formatter(nullfmt)

    #Sets up annotation for right y axis.
    bt_twin = bt_axis.twinx()
    bt_twin.set_yscale("log")
    bt_twin.set_ylim(ylimList[1][0],ylimList[1][1])
    bt_yticks = []
    bt_yticks.append(ylimList[1][0])
    for l in range(10,ylimList[1][1],10):
        if l != ylimList[1][0]:
            bt_yticks.append(l)
    if bt_yticks[-1] != ylimList[1][1]:
        bt_yticks.append(ylimList[1][1])
    bt_twin.set_yticks(bt_yticks)

    #Clear ticks on y axis to account for software issue of overlapping axes.
    bt_twin.yaxis.set_minor_formatter(nullfmt)

    #Set formatting for y axes
    bt_axis.yaxis.set_major_formatter(FormatStrFormatter('%d'))
    bt_twin.yaxis.set_major_formatter(FormatStrFormatter('%d'))

    #Set labels for y axes
    bt_axis.set_ylabel("$$\mathrm{10^3\hspace{2pt}people\hspace{2pt}per\hspace{2pt}km^2}$$",family='sans-serif')
    bt_twin.set_ylabel("$$\mathrm{10^3\hspace{2pt}people\hspace{2pt}per\hspace{2pt}km^2}$$",rotation=270,verticalalignment='bottom',family='sans-serif')

    #Save plot as PNG image
    fig.savefig(os.path.join(os.path.split(ifile_path)[0],'{:s}_PD_log.png'.format(opic_string)),dpi=300)
    #Show plot
    plt.show()


#This is where user specifies input file.
input_file = sys.argv[1]
input_file_handle = open(input_file,'r',encoding="latin-1")
input_file_path = os.path.split(input_file)[0]

#This specifies summary file
summary_output_file = "{:s}".format(os.path.join(input_file_path,''.join(['regional_location_summary',os.path.splitext(input_file)[1]])))
summary_output_file_handle = open(summary_output_file,'w')

#This specifies Bootstrap Output file
bstrap_output_file_handle = pandas.ExcelWriter("{:s}".format(os.path.join(input_file_path,''.join(['regional_location_bstrap',".xlsx"]))))

#Read in Data
file_data = input_file_handle.read()
input_file_handle.close()

#Split data into lines, and get rid of blank lines.
file_lines = file_data.split("\n")
while file_lines.count('') > 0:
    file_lines.remove('')
while file_lines.count(' ') > 0:
    file_lines.remove(' ')

#Get rid of header line, so that all that remains are data.
title_line = file_lines.pop(0)

#Split all lines by commas.
data_items = [x.split(",") for x in file_lines]
#Sets presribed order of regions to display on plot.
region_unique = ["N Am","CS Am","Europe","Africa","SW Asia","SC Asia","India","China","E Asia","SE Asia"]

#Sets lables for regions.
label_dict = {
    "N Am":"North America",
    "CS Am":"Latin America",
    "Europe":"Europe",
    "Africa":"Africa",
    "SW Asia":"Southwest Asia",
    "SC Asia":"Central-South Asia",
    "India":"India",
    "China":"China",
    "E Asia":"East Asia",
    "SE Asia":"Southeast Asia"
}

#Set up regions data structure (list of lists of lists).
regions = []
for region in region_unique:
    regions.append([data_line for data_line in data_items if data_line[2] == region])

#Establish each size class, all, above 2 million, and below 2 million.
allregions = copy.deepcopy(regions)
aboveregions = [[x for x in region_line if float(x[8]) > 2000.0] for region_line in allregions]
belowregions = [[x for x in region_line if float(x[8]) <= 2000.0] for region_line in allregions]

##Set y limits
ylimList = [(0,12),(1,60)]
##Create linear plot of changes in population vs urban expansion and population density for all cities.
bs_pack1,bs_pack2,region_means = plot_linear(allregions,region_unique,label_dict,input_file,summary_output_file_handle,bstrap_output_file_handle,'regional_all_location',4,ylimList)
ylimList = [(0.1,12),(1,60)]
##Create log plot of changes in population and urban expansion.
plot_log(allregions,region_unique,label_dict,input_file,'regional_all_location',4,ylimList,bs_pack1,bs_pack2,region_means)
ylimList = [(0,12),(1,60)]
##Create linear plot of changes in population vs urban expansion and population density for all cities above 2 million.
bs_pack1,bs_pack2,region_means = plot_linear(aboveregions,region_unique,label_dict,input_file,summary_output_file_handle,bstrap_output_file_handle,'regional_above_location',4,ylimList)
ylimList = [(0.1,12),(1,60)]
##Create log plot of changes in population and urban expansion for all cities above 2 million.
plot_log(aboveregions,region_unique,label_dict,input_file,'regional_above_location',4,ylimList,bs_pack1,bs_pack2,region_means)
ylimList = [(0,12),(1,60)]
##Create linear plot of changes in population vs urban expansion and population density for all cities below 2 million.
bs_pack1,bs_pack2,region_means = plot_linear(belowregions,region_unique,label_dict,input_file,summary_output_file_handle,bstrap_output_file_handle,'regional_below_location',4,ylimList)
ylimList = [(0.1,12),(1,60)]
##Create log plot of changes in population and urban expansion for all cities below 2 million.
plot_log(belowregions,region_unique,label_dict,input_file,'regional_below_location',4,ylimList,bs_pack1,bs_pack2,region_means)

#Close summary output file handle
summary_output_file_handle.close()
bstrap_output_file_handle.save()
#Restore codepage. This is depdendent on the MS-DOS version of chcp.
subprocess.Popen(['chcp',str(msg)],shell=True,stdout=subprocess.PIPE)
