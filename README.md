# performance-evolution-study

This repository contains the used files for my Bachelor thesis 'An Empirical Study on Static Performance Evolution in Open Source Software'. 
In my thesis, I used the static analysis tool [Infer](https://github.com/facebook/infer) to analyze open source Java projects found on Github. Therefore, Infer is needed to execute and replicate my work.

The scripts are seperated (exactly like my study) in Pilot Study (small-scale analysis) and 100k Analysis (large-scale analysis).
Note that some of the things that are automatically done in the 100k Analysis project (e.g. creating new directories), need to be done manually in the Pilot Study, as the pilot study only featured 8 projects and therefore did not need automation.

## Setup 

### Infer
A working version of [Infer](https://github.com/facebook/infer) is required. Infer can be installed from source or from the [official Infer website](https://fbinfer.com/)

### Linux
Since Infer only works on Linux, it is necessary to run the files on a Linux machine.

### Project structure
In my analysis, I had a *project* folder, a *result* folder, and a *database* folder.

The *project* folder is the directory where the git projects are cloned.

The *results* folder contains the generated costs reports of Infer. 

The *database* folder contains the database (and the Python files associated with reportings to get results from the database).

As in my automated script, the files are often moved from the project folder to the result folder for example, it is important to check, that the project strucutre is correct and that files are executed in the right directory (relative to the path). Otherwise, errors can easily  occur.

## Execution of project

### Generating costs reports

At first, the costs reports need to be generated. This is done using the **infer_executor.py** file in the pilot study or the **100k_crawler.py** file for the 100k Analysis. The first file needs to be given a manual list of repository names (the repository should exist in ./projects) and the second one uses the [**JAigantic**](https://mondego.ics.uci.edu/projects/SourcererJBF/#) dataset to run an automated analysis. 

Both scripts move the generated costs reports from the projects folder to the results folder.

### Creating the database

In the next step, the **databasecreation.py** needs to be executed to create the database. It is an SQLLite3 database.

### Mapping the costs

The **cost_report_mapper** (Pilot) or **different_costs_mapper_100k.py** need to be executed to map the generated costs reports from the projects/releases into the database.
This fills the Release and Function table with data

### Differential Costs Mapping

Infer's differential mode is executed in the ./results folder where the costs reports are located. For two subsequent versions, the differential mode is executed and the folder is named version-prior___version-after.
This is done using the **diff_report_executor.py** 

### Create Change Table
The **add_change_table_100k.py** needs to be executed to create the change table

### Fill Change Table with data
 
After the differential reports are created, the **differential_analysis_from_database.py** is executed, that compares changes detected by the 'Function' table only to Changes of the differential mode. If the change is found, the reasons as well as the maximum level is stored. Otherwise, the reason and level are Null, but the change is still entered.

Then the second file **differential_analysis_from_diffmode.py**, that compares the Changes of Infer's differential mode with the chagnes detectected using the 'Function' table needs to be executed.

### Analyze unknown functions (only 100k Analysis)

For changes whose reason/level is null, the **analyze_unknown_functions.py** can be executed to get the remaining reasons. If the reason was detected by Infer, infer_detected is True in the Change table. Otherwise infer_detected is false.

## Reporting

Using **change_report.py** or **change_report_100k.py**, information on the Changes are printed. **report_100k.py** excludes the 'Change' table and only focuses on reports based on the database.

With the **function_traze_analyzer.py** file, information on the functions is printed. This information includes statements on the reason/level of performance related code that causes the method to be non-constant.
  
