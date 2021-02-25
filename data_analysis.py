import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.graph_objects as go
from collections import Counter

# ---------------------- BEGIN CHART TYPES ----------------------
def plot_piechart(data_lst):
    # Remove all unneccessary lines. 
    data_lst = [item for item in data_lst if str(item) != "nan" and not item.startswith("-")]   

    # Count all occurances in the list and make a dataframe. 
    data_dict = Counter(data_lst)

    # Sort it based on value from high - low
    data_dict = dict(sorted(data_dict.items(), key=lambda item: item[1], reverse=True))

    fig = go.Figure(
        data=[
            go.Pie(
                labels=list(data_dict.keys()),
                values=list(data_dict.values()), 
                textinfo='label+value+percent',
                insidetextorientation='radial'
            )
        ]
    )

    # Style the piechart.
    fig.update_traces(hoverinfo='label+percent', textinfo='label+value+percent', textfont_size=20, marker=dict(line=dict(color='#000000', width=2)))
    fig.show()

def plot_bargraph(tot_dict, x_axis_title, y_axis_title):
    # Sort the data from high - low, based on value
    tot_dict = dict(sorted(tot_dict.items(), key=lambda item: item[1], reverse=False))

    # Add custom x and y-axis labels and change font-size. 
    fig = px.bar(x=list(tot_dict.values()), y=list(tot_dict.keys()), title="Long-Form Input")
    fig.update_layout(
        title="_",
        xaxis_title=x_axis_title,
        yaxis_title=y_axis_title,
        font=dict(
            size=12
        )
    )
    fig.show() 

def plot_bubble_scatter(new_data_df, x_axis_title, y_axis_title):
    total_df = pd.DataFrame({
        "type": [],
        "count": [],
        "year": []
    })

    for year_i in new_data_df.year.unique():
        yearly_data = new_data_df[new_data_df.year.eq(year_i)]
        counts = yearly_data["type"].value_counts().reset_index(name='count')

        counts["year"] = [year_i] * len(counts)       
        counts = counts.rename(columns={"index": "type"})
        total_df = pd.concat([total_df, counts], axis=0)

    fig = go.Figure(
        data=[
            go.Scatter(
                x=total_df["year"],
                y=total_df["type"],
                text=total_df["count"],
                mode='markers+text',
                marker=dict(                    
                    size=list(map(set_size, total_df["count"])),
                    colorscale="Viridis"
                )
            )
        ]
    )        

    # Add custom x and y-axis labels and change font-size.
    fig.update_layout(
        title="_",
        xaxis_title=x_axis_title,
        yaxis_title=y_axis_title,
        font=dict(
            size=12
        )
    )

    fig.show()    


def set_size(count):
    base_len = 20
    return base_len + (count * 2)

# ---------------------- END CHART TYPES ----------------------

# ---------------------- BEGIN RQ1 CODE ----------------------

def create_publication_venue(data):
    new_data_df = pd.DataFrame({
        "id": data["Unnamed: 0"],
        "venue": data["Publication Venue(RQ1)"]
    })    
    
    list_names = new_data_df['venue'].to_list()

    for venue in list(set(list_names)):
        new_id = new_data_df.loc[new_data_df['venue'] == venue, 'id']
        print("{} & {} & {} \\\\ \\hline".format(venue, ",".join(new_id), len(new_id)))            
        print("\n") 

def create_publication_year_and_type(data):
    new_data_df = pd.DataFrame({
        "type": data["Publication Type(RQ1)"].str.lower().str.capitalize(),
        "year": data["Year(RQ1)"]
    })

    temp_counter = Counter(new_data_df["type"].to_list())
    
    for key, val in temp_counter.items():
        print(key, val)
    

    new_data_df = new_data_df[(new_data_df["year"] >= 2012) & (new_data_df["year"] < 2020) ]

    plot_bubble_scatter(new_data_df, "Year", "Publication venue")        

def create_research_year_and_type(data):
    new_data_df = pd.DataFrame({
        "type": data["Research Strategy(RQ1)"].str.lower().str.capitalize(),
        "year": data["Year(RQ1)"]
    })

    new_data_df = new_data_df[(new_data_df["year"] >= 2012) & (new_data_df["year"] < 2020) ]

    plot_bubble_scatter(new_data_df, "Year", "Research strategy")            

def create_publication_type(data):
    pub_lst = data["Publication Type(RQ1)"].str.lower().str.capitalize().to_list()
    pub_dict = Counter(pub_lst)
    plot_bargraph(pub_dict, "Count", "Publication type")

def create_research_strategy(data):
    research_strat = data["Research Strategy(RQ1)"].str.lower().str.capitalize().to_list()
    res_dict = Counter(research_strat)
    plot_bargraph(res_dict, "Count", "Research type")

# ---------------------- END RQ1 CODE ----------------------

# ---------------------- BEGIN RQ2 CODE ----------------------
def tactic_correlation(data):
    new_data_df = {
        'p_id': data["ID"] ,
        'tactics': data["Tactics"]
    }
    tot_dict = {}
    
    paper_index = 0
    # while count < 98:
    for val in new_data_df["tactics"]:
        for sub_val in val.splitlines():
            if sub_val.startswith("-"):
                sub_val = sub_val[1:].strip().lower().capitalize()
                if sub_val in tot_dict.keys():
                    tot_dict[sub_val].append(paper_index)
                else:
                    tot_dict[sub_val] = [paper_index]
        paper_index += 1                           
                       

    # for i in new_data_df['p_id'].to_list():
        # print(new_data_df)
        # for val in new_data_df["tactics"][i].splitlines():
            # pass
        #     if val.startswith("-"):
        #         val = val[1:].strip().lower().capitalize()
        #         if val in tot_dict.keys():
        #             tot_dict[val].append(i)
        #         else:
        #             tot_dict[val] = [i]     

    # return    
    

    tot_dict = {key.split("(")[0].strip(): val for key, val in tot_dict.items() if len(val) >= 10}

    temp_sub_arr = []
    corr_dict = {}

    for key_1 in tot_dict.keys():
        for key_2 in tot_dict.keys():
            temp_sub_arr, go = check_for_comp(key_1, key_2, temp_sub_arr)
            if go:
                corr_dict[key_1 + " - " + key_2] = list(set(tot_dict[key_1]).intersection(tot_dict[key_2]))

    corr_dict = {key: val for key, val in corr_dict.items() if len(val) >= 10}
    corr_dict = dict(sorted(corr_dict.items(), key = lambda item: len(item[1]), reverse=True))

    most_used = ["Authentication",
                "Heartbeat",
                "Authorization",
                "Rollback",
                "Voting",
                "Ping/echo",
                "Active redundancy",
                "Passive redundancy",
                "Exception detection",
                "Limit access",
                "State resynchronization",
                "Limit exposure",
                "Transactions",
                "Audit trail",
                "Spare",
                "Verify message integrity",
                "Encapsulation",
                "Intrusion detection",
                "Redundancy",
                "Abstract common services",
                "Shadow",
                "Encrypt data",
                "Identify actors"]

    corr_dict = {key: val for key, val in corr_dict.items() if key.split("-")[0].strip() in most_used and key.split("-")[1].strip() in most_used}

    # Uncomment this to show the latex code for the common architectural tactics. 
    for key, val in corr_dict.items():
        print("{} & {} & {} \\\\ \\hline".format(key.split("-")[0].strip(), key.split("-")[1].strip() , len(val)))

def check_for_comp(key_1, key_2, temp_sub_arr):
    if key_1 == key_2:
        return temp_sub_arr, False

    for sub_arr in temp_sub_arr:
        if key_1 in sub_arr and key_2 in sub_arr:
            return temp_sub_arr, False

    temp_sub_arr.append([key_1, key_2])

    return temp_sub_arr, True

def tactic_mapping(data):

    lst_tactics = data["Tactics"].to_list()
    new_lst = []

    for item in lst_tactics:
        for val in item.splitlines():
            if val.startswith('-'):
                new_lst.append(val[1:].strip().lower().capitalize())

    none_word = "NONE"

    tot_dict = {
        "Performance" : {}, 

        "Compatibility": {
            "Interoperability": {}
        },

        "Usability": {},

        "Reliability": {
            "Availability": {}
        },

        "Security": {
            "Accountability": {}
        },

        "Maintainability" : {
            "Modifiability": {},
            "Reusability": {},
            "Testability": {}
        }, 

        "Portability": {
            "Adaptability": {}
        }
    }

    for key in tot_dict.keys():
        tot_dict[key][none_word] = {} 

    for item in new_lst:
        if "(" not in item:
            continue

        at, qa = item.split("(")
        at = at.strip().capitalize()
        qa = qa.strip().capitalize()

        qa = qa[:-1]

        for_temp_lst = []

        if "," in qa:
            for qa_sub in qa.split(","):
                qa_sub = qa_sub.strip().capitalize()
                for_temp_lst.append(qa_sub)
        else:             
            for_temp_lst.append(qa)            

        for qa_key in for_temp_lst:
            found = False
            if qa_key in tot_dict.keys():
                found = True
                if at in tot_dict[qa_key][none_word].keys():
                    tot_dict[qa_key][none_word][at] += 1
                else:
                    tot_dict[qa_key][none_word][at] = 1                    
                    
            else:
                for key in tot_dict.keys():
                    if qa_key in tot_dict[key].keys():
                        found = True
                        if at in tot_dict[key][qa_key].keys():
                            tot_dict[key][qa_key][at] += 1         
                        else:
                            tot_dict[key][qa_key][at] = 1  

            if found == False:
                tot_dict[qa_key] = {none_word : {}}      
                tot_dict[qa_key][none_word][at] = 1             

    tot_dict = dict(sorted(tot_dict.items(), reverse=False))

    for key, val in tot_dict.items():
        for sub_key in val.keys():
            tot_dict[key][sub_key] = dict(sorted(tot_dict[key][sub_key].items(), key=lambda item: item[1], reverse=True))

        if len(val) > 1:
            for sub_key, sub_val in val.items():
                if sub_key != none_word:
                    for sub_sub_key, sub_sub_val in sub_val.items():
                        if sub_sub_key in tot_dict[key][none_word].keys():
                            del tot_dict[key][none_word][sub_sub_key]
            
    tempie_dict = {}
    count_qa_at_dict = {}
    
    for key, val in tot_dict.items():
        for sub_key, sub_val in val.items():
            count = 0
            for sub_sub_key, sub_sub_val in sub_val.items():
                # print("{} & {} & {} & {} \\\\ \\hline".format(key, sub_key, sub_sub_key, sub_sub_val)) 
                if sub_sub_key in tempie_dict.keys():
                    tempie_dict[sub_sub_key] += sub_sub_val
                else:
                    tempie_dict[sub_sub_key] = sub_sub_val                                          

                # if ")" in key:
                    # print(key, sub_key, sub_sub_key, sub_sub_val)

                # Sometimes the encoding messes up and creates a )_x000b at the end, this fixes that.
                if ")" in key:
                    key = key.split(")")[0].strip()

                if key in count_qa_at_dict.keys():
                    count_qa_at_dict[key][0] += 1
                    count_qa_at_dict[key][1] += sub_sub_val
                else:
                    count_qa_at_dict[key] = [1, sub_sub_val]                                        

    # Uncomment this part to display all the tactics and to which sub-characteristic of the ISO25010 quality attributes they belong to.
    # for key, val in tot_dict.items():
        # print(key, val)
        # print("---")

    tempie_dict = dict(sorted(tempie_dict.items(), key=lambda item: item[1], reverse=True))

    # Uncommen this part to show all the tactics and how often they occured accross the primary studies. 
    for key, val in tempie_dict.items():
        if val >= 10:
            print("{} & {} \\\\ \\hline".format(key, val))
        

    count_qa_at_dict = dict(sorted(count_qa_at_dict.items(), key=lambda item:item[1][1], reverse=True))

    # plot_bargraph(count_qa_at_dict, "Count", "Quality attribute")

    # Uncommen this part to create latex code consisting of: the quality attribute, amount of unique tactics, amount of total tactic mentions. 
    # for key, val in count_qa_at_dict.items():
        # print("{} & {} & {} \\\\ \\hline".format(key, val[0], val[1]))        
          
                
def tactic_tradeoff(data):
    trade_off_lst = data["Tradeoff QA's (RQ2)"].to_list()
    trade_off_lst = [item for item in trade_off_lst if str(item) != "nan" and str(item) != "NONE - NONE"]
    temp_dict = {}

    for sub_trade_off_lst in trade_off_lst:
        for trade_off in sub_trade_off_lst.splitlines():

            if "-" in trade_off: 
                temp = trade_off.split("-")
            elif "~" in trade_off:
                temp = trade_off.split("~")                
            else:
                continue

            if temp[0] not in temp_dict.keys():
                temp_dict[temp[0]] = []     

            for i in range(1, len(temp)):
                temp_dict[temp[0]].append(temp[i])

    # Uncomment this to create latex table code for which quality attributes comes up in trade-offs accross the primary studies. 
    for key, val in temp_dict.items():
        for item in val:
            print("{} & {} \\\\ \\hline".format(key.strip(), item.strip()))                   
  

    print(count)

    qa_trade_off_lst = data["QA Tradeoff? (RQ2)"].to_list()

    qa_trade_off_dict = Counter(qa_trade_off_lst)

    plot_bargraph(qa_trade_off_dict, "Count", "Trade-off")          

# ---------------------- END RQ2 CODE ----------------------

# ------------ BEGIN PARAMETERS NOT CHOSEN CODE ------------
def create_architectural_style(data_df):
    arch_style_lst = data_df["Architectural Style(RQ2)"].str.strip().to_list()
    arch_style_dict = Counter(arch_style_lst)

    plot_bargraph(arch_style_dict, "a", "b")

def create_application_domain(data_df):
    domains = data_df["Application Domain(RQ2)"].str.strip().to_list()
    unique_domains = set(domains)
    # for domain in unique_domains:
        # print(domain)
    
    domains_count = Counter(domains)
    domains_count = dict(sorted(domains_count.items(), key = lambda item: item[1], reverse=True))
    for key, val in domains_count.items():
        print(key, val)

def create_application_field(data_df):
    fields = data_df["Application Field (RQ3)"].str.strip().to_list()
    fields_dict = Counter(fields)

    # plot_bargraph(fields_dict, "a", "b")

def create_evidence_type(data):
    evi_type = data["Type of Evidence (RQ2)"].str.strip().to_list()
    evi_type_dict = Counter(evi_type)

    for key, val in evi_type_dict.items():
        temp = 100/98*val
        print("{} {} {}".format(key, val, temp))

    # plot_bargraph(evi_type_dict, "Count", "Evidence type")

# ------------ END PARAMETERS NOT CHOSEN CODE ------------
if __name__ == "__main__":
    xlsx_file = "ExtractedData.xlsx"
    data_df = pd.read_excel(xlsx_file, sheet_name="Data")
    data_par = pd.read_excel(xlsx_file, sheet_name="QAs")

    # Remove unnecessary columns introduced by the Google Sheet download.
    data_df = data_df.drop(data_df.iloc[:, 30:45], axis = 1) 
    
    # Remove the technical reports from the dataset
    data_df = data_df[data_df["Publication Type(RQ1)"] != "Technical report"]
    

    # RQ1
    # create_publication_venue(data_df)
    # create_publication_year_and_type(data_df)
    # create_publication_type(data_df)
    # create_research_year_and_type(data_df)
    # create_research_strategy(data_df)

    # RQ2
    tactic_mapping(data_df)
    # tactic_correlation(data_df)
    # tactic_tradeoff(data_df)

    # Not chosen parameters.
    # create_architectural_style(data_df)
    # create_application_domain(data_df)
    # create_application_field(data_df)
    # create_evidence_type(data_df)


    