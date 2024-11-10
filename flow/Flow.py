from graphviz import Digraph

# Example Flow Code
flowchart = Digraph("Flowchart", format="png")
flowchart.attr(rankdir="TB", size="8,10", splines="ortho", nodesep="0.8", ranksep="1")


flowchart.node("Begin", "Begin", shape="ellipse", width="1", height="0.7")
flowchart.node("UploadFile", "Upload file", shape="parallelogram", width="2", height="0.7")
flowchart.node("WebAPI", "Web UI/API store", shape="box", width="2.5", height="0.7")
flowchart.node("UploadCuckoo", "Upload file to Cuckoo host", shape="box", width="3", height="0.7")


with flowchart.subgraph(name="cluster_cuckoo") as cuckoo:
    cuckoo.attr(label="Cuckoo host", style="rounded", color="black", fontsize="10")
    cuckoo.node("RunGuest", "Run the Guest (VM) through Socket", shape="box", width="2.5", height="0.7")
    cuckoo.node("SendFile", "Send file to Guest", shape="box", width="2.5", height="0.7")
    cuckoo.node("StaticAnalysis", "Static Analysis", shape="box", width="2.5", height="0.7")
    cuckoo.node("Summary", "Summary and report", shape="box", width="2.5", height="0.7")
    cuckoo.node("Callback", "Run callback send task ID to Machine Learning", shape="box", width="2.5", height="0.7")


    cuckoo.edge("RunGuest", "SendFile")
    cuckoo.edge("StaticAnalysis", "Summary")
    cuckoo.edge("Summary", "Callback")


with flowchart.subgraph(name="cluster_guest") as guest:
    guest.attr(label="Guest", style="rounded", color="black", fontsize="10")
    guest.node("RunFile", "Run file", shape="box", width="2.5", height="0.7")
    guest.node("RecordBehavior", "Record Behaviors", shape="box", width="2.5", height="0.7")

    # Kết nối trong cụm Guest
    guest.edge("RunFile", "RecordBehavior")


flowchart.node("MachineLearning", "Machine Learning get report from Cuckoo host", shape="box", width="2.5", height="0.7")
flowchart.node("Detect", "Detect", shape="box", width="2", height="0.7")
flowchart.node("Output", "Output File Report", shape="ellipse", width="1.5", height="0.7")
flowchart.node("End", "End", shape="ellipse", width="1", height="0.7")


flowchart.edge("Begin", "UploadFile")
flowchart.edge("UploadFile", "WebAPI")
flowchart.edge("WebAPI", "UploadCuckoo")
flowchart.edge("UploadCuckoo", "RunGuest")
flowchart.edge("SendFile", "RunFile") 
flowchart.edge("RecordBehavior", "Summary") 
flowchart.edge("Callback", "MachineLearning")
flowchart.edge("MachineLearning", "Detect")
flowchart.edge("Detect", "Output")
flowchart.edge("Output", "End")


flowchart.render("taller_flowchart", view=True)
