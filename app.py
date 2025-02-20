import gradio as gr
import os
import pandas as pd
from datetime import datetime

# Folder untuk menyimpan file yang diupload
UPLOAD_FOLDER = "./upload"
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
        return df.iloc[:, -1].dropna().unique().tolist()  # Updated (Last Column)
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
    """Loads an ontology and extracts entities, data properties, and relationships using SPARQL queries."""
    g = Graph()
    try:
        g.parse(file_path, format="xml")  # Adjust format as needed

        # Extract entity names (classes)
        entities_query = """
        SELECT ?entity WHERE {
            ?entity a owl:Class .
        }
        """
        entities = {str(row[0].split("#")[-1]) for row in g.query(entities_query)}

        # Extract data properties
        data_props_query = """
        SELECT ?prop WHERE {
            ?prop a owl:DatatypeProperty .
        }
        """
        data_properties = {str(row[0].split("#")[-1]) for row in g.query(data_props_query)}

        # Extract relationships (Object Properties)
        relations_query = """
        SELECT ?relation WHERE {
            ?relation a owl:ObjectProperty .
        }
        """
        relations = {str(row[0].split("#")[-1]) for row in g.query(relations_query)}

        # Extract superclass-subclass relationships
        subclass_query = """
        SELECT ?subclass ?superclass WHERE {
            ?subclass rdfs:subClassOf ?superclass .
        }
        """
        subclass_relations = {(str(row[0].split("#")[-1]), str(row[1].split("#")[-1])) for row in g.query(subclass_query)}

        return entities, data_properties, relations, subclass_relations, None
    except Exception as e:
        return set(), set(), set(), set(), f"Error parsing ontology: {e}"

# Fungsi untuk membandingkan dua ontologi
def compare_ontologies(file1, file2):
    """Compares two ontology files based on SPARQL rules."""
    file1_path = os.path.join(UPLOAD_FOLDER, file1)
    file2_path = os.path.join(UPLOAD_FOLDER, file2)

    if not os.path.exists(file1_path) or not os.path.exists(file2_path):
        return [["Error: One or both files not found."]]

    entities1, data_props1, relations1, subclass1, error1 = parse_ontology(file1_path)
    entities2, data_props2, relations2, subclass2, error2 = parse_ontology(file2_path)

    if error1 or error2:
        return [[f"Error parsing files: {error1 or error2}"]]

    # Rule 1: Matched entities with data properties
    matched_entities = entities1.intersection(entities2)
    matched_data_props = data_props1.intersection(data_props2)

    # Rule 2: Matched data properties but different entity names
    common_data_props_diff_entities = {
        dp for dp in matched_data_props if dp not in matched_entities
    }

    # Rule 3: Matched relationships
    matched_relations = relations1.intersection(relations2)

    # Rule 4: Superclass-subclass relationships (File1 -> File2 and vice versa)
    subclass_in_file1_not_in_file2 = subclass1 - subclass2
    subclass_in_file2_not_in_file1 = subclass2 - subclass1

    # Prepare comparison results
    comparison_results = []

    # Matched Entities & Data Properties
    for entity in matched_entities:
        comparison_results.append([entity, "✔", "✔"])

    # Matched Data Properties but Different Entities
    for dp in common_data_props_diff_entities:
        comparison_results.append([dp, "✔ (Different Entities)", "✔ (Different Entities)"])

    # Matched Relationships
    for relation in matched_relations:
        comparison_results.append([relation, "✔", "✔"])

    # Superclass Relationships
    for subclass, superclass in subclass_in_file1_not_in_file2:
        comparison_results.append([f"{subclass} → {superclass}", "✔ (File1 only)", ""])

    for subclass, superclass in subclass_in_file2_not_in_file1:
        comparison_results.append([f"{subclass} → {superclass}", "", "✔ (File2 only)"])

    # Summary
    summary = {
        "Matched Entities": len(matched_entities),
        "Matched Data Properties": len(matched_data_props),
        "Data Properties (Different Entities)": len(common_data_props_diff_entities),
        "Matched Relationships": len(matched_relations),
        "Unique Superclass-Subclass File1": len(subclass_in_file1_not_in_file2),
        "Unique Superclass-Subclass File2": len(subclass_in_file2_not_in_file1),
        "Total Entities File1": len(entities1),
        "Total Entities File2": len(entities2),
        "Total Data Properties File1": len(data_props1),
        "Total Data Properties File2": len(data_props2),
        "Total Relations File1": len(relations1),
        "Total Relations File2": len(relations2)
    }

    return comparison_results, summary


    # Fungsi mengambil nama file saja tanpa ekstensi
def get_filename_without_extension(file_path):
    # Dapatkan nama file tanpa path
    file_name = os.path.basename(file_path)

    # Pisahkan nama file dan ekstensi
    name_without_ext, _ = os.path.splitext(file_name)

    return name_without_ext

# Fungsi untuk konversi file csv atau excel ke ontologi .owl
def convert_to_ontology(file, owner, date):
    if file is None or not (file.name.endswith(".csv") or file.name.endswith(".xlsx")):
        return "Error: Please upload a valid CSV or Excel file."

    try:
        # Baca file input
        if file.name.endswith(".csv"):
            df = pd.read_csv(file.name)
        else:
            df = pd.read_excel(file.name)

        # Konversi ke format .owl sederhana (mockup)
        ontology_content = "<?xml version='1.0'?>\n<rdf:RDF xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\">\n"
        for _, row in df.iterrows():
            ontology_content += f"  <rdf:Description rdf:about=\"{row[0]}\">\n"
            for col, value in row.items():
                ontology_content += f"    <{col}>{value}</{col}>\n"
            ontology_content += "  </rdf:Description>\n"
        ontology_content += "</rdf:RDF>"

        # Simpan file .owl
        output_file = os.path.join(UPLOAD_FOLDER, get_filename_without_extension(file)+"_"+f"converted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.owl")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(ontology_content)
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
            file_input = gr.File(label="Upload CSV or Excel File")
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

            #preview_button.click(preview_ontology, inputs=[ontology_file], outputs=[file_preview])

            preview_button.click(
                lambda table: view_ontology_content(get_selected_file(table)),
                inputs=[ontology_table],
                outputs=[ontology_content],
            )

        with gr.Tab("Perbandingan Ontologi"):
              gr.Markdown("## Perbandingan Ontologi")

              # Dropdowns for ontology selection
              file1_dropdown = gr.Dropdown(choices=list_compared_ontologies(), label="Select First Ontology")
              file2_dropdown = gr.Dropdown(choices=list_compared_ontologies(), label="Select Second Ontology")

              # Buttons
              compare_button = gr.Button("Bandingkan")
              clear_button = gr.Button("Clear")

              # Outputs: Comparison Table and Summary
              comparison_table = gr.Dataframe(headers=["Entity/Relation", "In Ontology 1", "In Ontology 2"], interactive=False)
              summary_output = gr.Textbox(label="Summary", interactive=False, lines=5)

              # Function to clear selection and results
              def clear_comparison():
                return None, None, [], ""

              # Connect buttons to functions
              compare_button.click(
                  compare_ontologies,
                  inputs=[file1_dropdown, file2_dropdown],
                  outputs=[comparison_table, summary_output]
              )

              clear_button.click(clear_comparison, outputs=[file1_dropdown, file2_dropdown, comparison_table, summary_output])
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
