
from common import LoadGoodDataSdk, csv_to_sql

import streamlit as st
import streamlit.components.v1 as components

# Function to generate graph
def generate_graph(data):
    graph = graphviz.Digraph()

    root = data['title']
    # Create nodes for each section
    for section in data['content']['layout']['sections']:  # IDashboardLayoutSection
        for item in section['items']:  # IDashboardLayoutItem
            graph.edge(root, item['widget']['insight']['identifier']['id'])
            root = item['widget']['insight']['identifier']['id']

    return graph


def main():
    # session variables
    if "analytics" not in st.session_state:
        st.session_state["analytics"] = []
    if "gd" not in st.session_state:
        st.session_state["gd"] = LoadGoodDataSdk(st.secrets["GOODDATA_HOST"], st.secrets["GOODDATA_TOKEN"])
    
    st.set_page_config(
        layout="wide", page_icon="favicon.ico", page_title="Streamlit-GoodData integration demo"
    )

    my_html = f"""
    <script>
        console.log("#PARENT: Setup parent message listener");
        window.addEventListener(
            "message",
            function (e) {{
                console.log("#PARENT: Post message received", e.data.gdc.event)
                if (e.data.gdc.event.name == "listeningForApiToken"){{
                    const postMessageStructure = {{
                        gdc: {{
                            product: "dashboard",
                            event: {{
                                name: "setApiToken",
                                data: {{
                                    token: "{st.secrets["GOODDATA_TOKEN"]}"
                                }}
                            }}
                        }}
                    }};
                    console.log("#PARENT: Sending token to embedded window", postMessageStructure);
                    
                    const origin = "*";
                    const iframe = document.getElementById("embedded-content").contentWindow;
                    iframe.postMessage(postMessageStructure, origin);
                }}
            }},
            false
        ); 
    </script>
    """

    with st.sidebar:
        st.write("ESG Demo Content presented by GoodData")
        ws_list = st.selectbox("Select area of interest", options=[w.name for w in st.session_state["gd"].workspaces])
        st.session_state["analytics"] = st.session_state["gd"].details(wks_id=ws_list, by="name")
        ws_dash_list = st.selectbox("Select a dashboard", [d.title for d in st.session_state["analytics"].analytical_dashboards])
        embed_dashboard = st.button("Embed dashboard")
        display_dashboard = st.button("Display details")
    
    active_ws = st.session_state["gd"].specific(ws_list, of_type="workspace", by="name")
    if embed_dashboard:
        active_dash = st.session_state["gd"].specific(ws_dash_list, of_type="dashboard", by="name", ws_id=active_ws.id)
        st.write(f"connecting to: {st.secrets['GOODDATA_HOST']}/dashboards/embedded/#/workspace/{active_ws.id}/dashboard/{active_dash.id}?apiTokenAuthentication=true&showNavigation=false&setHeight=700")
        components.html(my_html)
        components.iframe(
            f"{st.secrets['GOODDATA_HOST']}/dashboards/embedded/#/workspace/{active_ws.id}/dashboard/{active_dash.id}?showNavigation=false&setHeight=700", 1400, 1500, scrolling=True)
    elif display_dashboard:
        #active_dash = st.session_state["gd"].specific(ws_dash_list, of_type="dashboard", by="name", ws_id=active_ws.id)
        #st.write(f"Selected dashboard: {active_dash}")
        #dashboard_visual = generate_graph(active_dash.to_dict())
        dashboard_visual = st.session_state["gd"].schema(ws_dash_list, ws_id=active_ws.id)
        st.graphviz_chart(dashboard_visual)
    else: 
        st.write(f"Selected workspace: {active_ws}")
        
        
    
if __name__ == "__main__":
    main()
