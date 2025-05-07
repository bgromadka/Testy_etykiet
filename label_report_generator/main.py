import os
from datetime import datetime

from label_report_generator.report_generator import LabelReportGenerator


if __name__ == "__main__":
    script_directory = os.path.dirname(os.path.abspath(__file__))
    labels_folder = os.path.join(script_directory, 'input_labels_folder')
    output_filename = f"Label_validation_report_{datetime.now().strftime('%d-%m-%Y')}.docx"

    generator = LabelReportGenerator(
        input_labels_folder=labels_folder,
        output_docx=output_filename,
        number_of_columns_per_page=3,
        max_rows_per_page=2
    )
    generator.generate()
