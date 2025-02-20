## ini yang ok final

import gradio as gr
import os
import pandas as pd
from rdflib import Graph, Namespace, RDF, RDFS, OWL
from datetime import datetime

# Folder untuk menyimpan file yang diupload
UPLOAD_FOLDER = "/content/drive/MyDrive/SDI"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Fungsi untuk menampilkan isi file .owl
def preview_ontology(file):
    if file is None:
        return "No file uploaded."
    if not file.name.endswith(".owl"):
        return "Invalid file type. Please upload an .owl file."

    try:
        with open(file.name, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {e}"

# Fungsi untuk menyimpan hasil input ke CSV
def submit_ontology(name, owner, date, file):
    if file is None or not file.name.endswith(".owl"):
        return "Error: No valid .owl file uploaded."

    try:
        # Simpan file di folder upload
        file_path = os.path.join(UPLOAD_FOLDER, os.path.basename(file.name))
        with open(file_path, "wb") as f:
            f.write(file.encode("utf-8"))

        # Simpan metadata ke CSV
        data = {
            "Ontology Name": [name],
            "Owner": [owner],
            "Creation Date": [date],
            "File Name": [file_path],
        }
        df = pd.DataFrame(data)
        csv_path = os.path.join(UPLOAD_FOLDER,"upload_ontologi.csv")
        if os.path.exists(csv_path):
            df.to_csv(csv_path, mode="a", header=False, index=False)
        else:
            df.to_csv(csv_path, index=False)

        return "Ontology and metadata successfully uploaded and saved!"
    except Exception as e:
        return f"Error saving file or metadata: {e}"

# Fungsi untuk menampilkan daftar ontologi
def list_compared_ontologies():
    csv_path = os.path.join(UPLOAD_FOLDER,"upload_ontologi.csv")
    if not os.path.exists(csv_path):
        return []

    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            return []  # Return empty list if no data
        return df.iloc[:, 0].dropna().unique().tolist()  # Updated (Last Column)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []

def list_ontologies():
    csv_path = os.path.join(UPLOAD_FOLDER,"upload_ontologi.csv")
    if not os.path.exists(csv_path):
        return []

    try:
        df = pd.read_csv(csv_path)
        return df.values.tolist()
    except Exception as e:
        return []




# Fungsi untuk membaca entitas dan relasi dari file OWL sederhana
def parse_ontology(file_path):
    entities = set()
    relations = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            if "rdf:Description" in line:
                entities.add(line.strip())
            elif "<" in line and "/>" in line:
                relations.add(line.strip())
    except Exception as e:
        return entities, relations, str(e)
    return entities, relations, None

# Fungsi untuk membandingkan dua ontologi
def compare_ontologies(file1, file2):
    file1_path = os.path.join(UPLOAD_FOLDER, file1)
    file2_path = os.path.join(UPLOAD_FOLDER, file2)

    if not os.path.exists(file1_path) or not os.path.exists(file2_path):
        return [["Error: One or both files not found."]]

    entities1, relations1, error1 = parse_ontology(file1_path)
    entities2, relations2, error2 = parse_ontology(file2_path)

    if error1 or error2:
        return [[f"Error parsing files: {error1 or error2}"]]

    common_entities = entities1.intersection(entities2)
    common_relations = relations1.intersection(relations2)

    comparison_results = []
    for entity in entities1.union(entities2):
        comparison_results.append([
            entity, "Yes" if entity in entities1 else "No", "Yes" if entity in entities2 else "No"
        ])
    for relation in relations1.union(relations2):
        comparison_results.append([
            relation, "Yes" if relation in relations1 else "No", "Yes" if relation in relations2 else "No"
        ])

    # Create summary dictionary
    summary = {
        "Common Entities": len(common_entities),
        "Common Relations": len(common_relations),
        "Total Entities in File 1": len(entities1),
        "Total Entities in File 2": len(entities2),
        "Total Relations in File 1": len(relations1),
        "Total Relations in File 2": len(relations2)
    }

    # Generate formatted markdown table
    summary_table = "### Ontology Comparison Summary\n"
    summary_table += "| Metric                     | Value |\n"
    summary_table += "|----------------------------|-------|\n"
    for key, value in summary.items():
        summary_table += f"| {key} | {value} |\n"


    return comparison_results, summary_table


    # Fungsi mengambil nama file saja tanpa ekstensi
def get_filename_without_extension(file_path):
    # Dapatkan nama file tanpa path
    file_name = os.path.basename(file_path)

    # Pisahkan nama file dan ekstensi
    name_without_ext, _ = os.path.splitext(file_name)

    return name_without_ext

# Function to read and preview an ontology file
def view_ontology_content(file_path):
    if not file_path or not os.path.exists(file_path):
        return "Error: File not found."

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content[:5000]  # Limiting to 5000 characters for display
    except Exception as e:
        return f"Error reading file: {e}"

# Function to get selected file path from the table
def get_selected_file(dataframe):
    if dataframe and isinstance(dataframe, list) and len(dataframe) > 0:
        return dataframe[0][-1]  # Last column contains file path
    return ""

# Fungsi untuk konversi file csv atau excel ke ontologi .owl
from rdflib import Graph, Namespace, RDF, RDFS, OWL
import pandas as pd

def csv_to_owl(csv_file_path, output_owl_path):
    """
    Converts a CSV file containing database schema information into an OWL ontology file.

    :param csv_file_path: Path to the input CSV file.
    :param output_owl_path: Path to save the generated OWL file.
    """
    # Load the CSV file
    #df_csv = pd.read_csv(csv_file_path)

    try:
        df_csv = pd.read_csv(csv_file_path, encoding="utf-8")
    except UnicodeDecodeError:
        df_csv = pd.read_csv(csv_file_path, encoding="ISO-8859-1")


    # Define the ontology namespace
    ontology_uri = "http://example.com/ontology#"
    ontology = Graph()
    ONTO = Namespace(ontology_uri)

    # Bind the namespace
    ontology.bind("onto", ONTO)

    # Add ontology metadata
    ontology.add((ONTO.Ontology, RDF.type, OWL.Ontology))

    # Process the CSV data to create ontology classes and properties
    for _, row in df_csv.iterrows():
        table_name = row["table_name"]
        column_name = row["column_name"]
        data_type = row["data_type"]
        constraint_type = row["constraint_type"]

        # Create Class for table if not exists
        class_uri = ONTO[table_name]
        ontology.add((class_uri, RDF.type, OWL.Class))

        # Create DatatypeProperty for column
        property_uri = ONTO[column_name]
        ontology.add((property_uri, RDF.type, OWL.DatatypeProperty))
        ontology.add((property_uri, RDFS.domain, class_uri))

        # Define Range based on Data Type
        datatype_mapping = {
            "bigint": "xsd:integer",
            "integer": "xsd:integer",
            "character varying": "xsd:string",
            "text": "xsd:string",
            "boolean": "xsd:boolean",
            "timestamp without time zone": "xsd:dateTime",
        }

        xsd_type = datatype_mapping.get(data_type, "xsd:string")
        ontology.add((property_uri, RDFS.range, Namespace("http://www.w3.org/2001/XMLSchema#")[xsd_type]))

        # Define Primary Key as unique identifier
        if constraint_type == "PRIMARY KEY":
            ontology.add((property_uri, RDF.type, OWL.FunctionalProperty))

    # Save the ontology to a file
    ontology.serialize(destination=output_owl_path, format="xml")

    return output_owl_path



def convert_to_ontology(file, owner, date):
    try:
        # Simpan file .owl
        output_file = os.path.join(UPLOAD_FOLDER, get_filename_without_extension(file)+"_"+f"converted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.owl")
        csv_file=os.path.join(UPLOAD_FOLDER, get_filename_without_extension(file)+f".csv")
        # Read the Excel file and convert to CSV
        df_excel = pd.read_excel(file)
        df_excel.to_csv(csv_file, index=False)

        csv_to_owl(csv_file, output_file)

        # Baca isi file .owl
        # Simpan file di folder upload
        file_path = os.path.join(UPLOAD_FOLDER, os.path.basename(file.name))
        with open(file_path, "wb") as f:
            f.write(file.encode("utf-8"))

        # Simpan metadata ke CSV
        data = {
            "Ontology Name": [get_filename_without_extension(file)+"_"+f"converted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.owl"],
            "Owner": [owner],
            "Creation Date": [date],
            "File Name": [output_file],
        }
        df = pd.DataFrame(data)
        csv_path = os.path.join(UPLOAD_FOLDER,"upload_ontologi.csv")
        if os.path.exists(csv_path):
            df.to_csv(csv_path, mode="a", header=False, index=False)
        else:
            df.to_csv(csv_path, index=False)
        return f"File converted successfully and saved to {output_file}!"
    except Exception as e:
        return f"Error during conversion: {e}"

# Function to merge ontologies
def merge_ontologies(file1, file2):
    file1_path = os.path.join(UPLOAD_FOLDER, file1)
    file2_path = os.path.join(UPLOAD_FOLDER, file2)

    if not os.path.exists(file1_path) or not os.path.exists(file2_path):
        return "Error: One or both ontology files not found."

    try:
        # Load both ontologies
        g1 = Graph()
        g2 = Graph()
        g1.parse(file1_path, format="xml")
        g2.parse(file2_path, format="xml")

        # Merge ontologies
        g1 += g2

        # Generate merged filename
        merged_filename = f"merged_{get_filename_without_extension(file1)}_{get_filename_without_extension(file2)}.owl"
        merged_file_path = os.path.join(UPLOAD_FOLDER, merged_filename)

        # Save merged ontology
        g1.serialize(destination=merged_file_path, format="xml")

        # Update metadata in CSV
        data = {
            "Ontology Name": [merged_filename],
            "Owner": ["Merged"],
            "Creation Date": [datetime.now().strftime("%Y-%m-%d")],
            "File Name": [merged_file_path],
        }
        df = pd.DataFrame(data)
        csv_path = os.path.join(UPLOAD_FOLDER, "upload_ontologi.csv")
        if os.path.exists(csv_path):
            df.to_csv(csv_path, mode="a", header=False, index=False)
        else:
            df.to_csv(csv_path, index=False)

        return f"Ontologies merged successfully and saved as {merged_filename}!"
    except Exception as e:
        return f"Error merging ontologies: {e}"

# Sistem Menu dengan Gradio
with gr.Blocks() as menu_ui:
    with gr.Row():
        gr.Markdown("# Ontology System Menu")
    with gr.Tabs():
        with gr.Tab("Upload"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("## Ontology Management - Upload")
                    ontology_name = gr.Textbox(label="Ontology Name")
                    owner_name = gr.Textbox(label="Owner Name")
                    creation_date = gr.Textbox(label="Creation Date", value=datetime.now().strftime("%Y-%m-%d"))
                    ontology_file = gr.File(label="Upload Ontology (.owl)")
                    submit_button = gr.Button("Submit")
                    preview_button = gr.Button("Preview")
                    clear_button = gr.Button("Clear")
                    result_output = gr.Textbox(label="Result", interactive=False)

                with gr.Column():
                    gr.Markdown("## File Preview")
                    file_preview = gr.Textbox(label="Ontology Content", lines=20, interactive=False)

            # Interaksi tombol di sub-menu Upload
            preview_button.click(preview_ontology, inputs=[ontology_file], outputs=[file_preview])
            submit_button.click(submit_ontology, inputs=[ontology_name, owner_name, creation_date, ontology_file], outputs=[result_output])

            # Fungsi untuk tombol Clear
            def clear_inputs():
                return "", "", datetime.now().strftime("%Y-%m-%d"), None, "", ""

            clear_button.click(clear_inputs, outputs=[ontology_name, owner_name, creation_date, ontology_file, file_preview, result_output])

        with gr.Tab("Konversi"):
            gr.Markdown("## Ontology Management - Konversi")
            #file_input = gr.File(label="Upload CSV or Excel File")
            file_input = gr.File(label="Upload CSV or Excel File", type="filepath")
            owner_input = gr.Textbox(label="Owner Name")
            date_input = gr.Textbox(label="Creation Date", value=datetime.now().strftime("%Y-%m-%d"))
            preview_button = gr.Button("Preview")
            clear_button = gr.Button("Clear")
            convert_button = gr.Button("Convert to Ontology")
            file_preview = gr.Textbox(label="File Preview", lines=20, interactive=False)
            conversion_result = gr.Textbox(label="Conversion Result", interactive=False)

            # Fungsi untuk tombol Clear di Konversi
            def clear_conversion_inputs():
                return None, "", datetime.now().strftime("%Y-%m-%d"), "", ""

            # Preview file CSV atau Excel
            def preview_file(file):
                if file is None:
                    return "No file uploaded."
                try:
                    if file.name.endswith(".csv"):
                        df = pd.read_csv(file.name)
                    elif file.name.endswith(".xlsx"):
                        df = pd.read_excel(file.name)
                    else:
                        return "Invalid file format."
                    return df.to_string()
                except Exception as e:
                    return f"Error reading file: {e}"

            preview_button.click(preview_file, inputs=[file_input], outputs=[file_preview])
            clear_button.click(clear_conversion_inputs, outputs=[file_input, owner_input, date_input, file_preview, conversion_result])
            convert_button.click(convert_to_ontology, inputs=[file_input, owner_input, date_input], outputs=[conversion_result])

        with gr.Tab("Daftar Ontologi"):
            gr.Markdown("## Daftar Ontologi")
            ontology_table = gr.Dataframe(headers=["Ontology Name", "Owner", "Creation Date", "File Name"], interactive=False)
            reload_button = gr.Button("Reload Ontologies")
            preview_button = gr.Button("Preview Selected Ontology")
            ontology_content = gr.Textbox(label="Ontology Content", lines=20, interactive=False)

            # Fungsi untuk memperbarui tabel
            def update_ontology_table():
                ontology_data = list_ontologies()
                return ontology_data

            # Hubungkan tombol Reload ke fungsi pembaruan tabel
            reload_button.click(update_ontology_table, outputs=[ontology_table])

            # Interaksi tombol Preview
            def get_selected_file(dataframe):
                if dataframe and isinstance(dataframe, list) and len(dataframe) > 0:
                    return dataframe[0][-1]  # Ambil kolom terakhir sebagai nama file
                return ""

            preview_button.click(
                lambda table: view_ontology_content(get_selected_file(table)),
                inputs=[ontology_table],
                outputs=[ontology_content],
            )

        with gr.Tab("Perbandingan Ontologi"):
            gr.Markdown("## Perbandingan Ontologi")

            # Show available ontologies as a DataFrame
            ontology_table = gr.Dataframe(value=list_compared_ontologies(), headers=["Ontology Name"], interactive=False)
            reload_button = gr.Button("Reload Ontologies")

            def update_ontology_table():
                ontology_data = list_ontologies()
                return ontology_data
                
            reload_button.click(update_ontology_table, outputs=[ontology_table])
            # Selection buttons
            ontology_input = gr.Textbox(label="Type Ontology Name (copy from table)", interactive=True)
            select_button_1 = gr.Button("Set as Ontology 1")
            select_button_2 = gr.Button("Set as Ontology 2")

            # Display selected ontologies
            selected_ontology_1 = gr.Textbox(label="Selected Ontology 1", interactive=False)
            selected_ontology_2 = gr.Textbox(label="Selected Ontology 2", interactive=False)

            # Buttons
            compare_button = gr.Button("Bandingkan")
            clear_button = gr.Button("Clear")

            # Outputs: Comparison Table and Summary
            comparison_table = gr.Dataframe(headers=["Entity/Relation", "In Ontology 1", "In Ontology 2"], interactive=False)
            #summary_output = gr.Textbox(label="Summary", interactive=False, lines=5)
            #summary_output = gr.Dataframe(headers=["Metric", "Count"], interactive=False)
            summary_output = gr.Markdown()

            # Button clicks to set ontology selection
            select_button_1.click(lambda x: x, inputs=[ontology_input], outputs=[selected_ontology_1])
            select_button_2.click(lambda x: x, inputs=[ontology_input], outputs=[selected_ontology_2])


            # Compare ontologies
            compare_button.click(
              compare_ontologies,
              inputs=[selected_ontology_1, selected_ontology_2],
              outputs=[comparison_table, summary_output]
            )

            # Clear selections and results
            clear_button.click(clear_comparison, outputs=[selected_ontology_1, selected_ontology_2, comparison_table, summary_output])

        with gr.Tab("Merge Ontology"):
            gr.Markdown("## Merge Two Ontologies")

            file1_dropdown = gr.Dropdown(choices=list_compared_ontologies(), label="Select First Ontology")
            file2_dropdown = gr.Dropdown(choices=list_compared_ontologies(), label="Select Second Ontology")

            merge_button = gr.Button("Merge Ontologies")
            clear_merge_button = gr.Button("Clear")

            merge_output = gr.Textbox(label="Merge Result", interactive=False, lines=5)

            # Function to clear selections
            def clear_merge():
                return None, None, ""

            # Connect button actions
            merge_button.click(
                merge_ontologies,
                inputs=[file1_dropdown, file2_dropdown],
                outputs=[merge_output]
            )

            clear_merge_button.click(
                clear_merge,
                outputs=[file1_dropdown, file2_dropdown, merge_output]
            )

# Jalankan aplikasi
if __name__ == "__main__":
    menu_ui.launch()
