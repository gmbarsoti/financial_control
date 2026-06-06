import os
import yaml


def create_yaml_file():
    article_info = [
        {
            'Ref_data': {
                'pdf_secret': ''
            }
        }
    ]
    yaml_path = os.path.join('.', 'statementSource', 'financial.yaml')
    with open(yaml_path, 'w') as yaml_file:
        data = yaml.dump(article_info, yaml_file)
        print("Write successful")


def update_ref_yaml(data_to_update, value):
    yaml_path = os.path.join('.', 'statementSource', 'financial.yaml')
    with open(yaml_path, "r") as yaml_file:
        data = yaml.load(yaml_file, Loader=yaml.FullLoader)
        data[0]['Ref_data'][data_to_update] = value
    with open(yaml_path, "w") as yaml_file:
        yaml.dump(data, yaml_file)


def get_from_ref_yaml(required_data: str, institution: str):
    yaml_path = os.path.join('.', 'statementSource', 'financial.yaml')
    with open(yaml_path, "r") as yaml_file:
        data = yaml.load(yaml_file, Loader=yaml.FullLoader)
    match institution.lower():
        case "inter":
            return data[0]['Ref_data'][required_data][:6]
        case "meliuz":
            return data[0]['Ref_data'][required_data]
    return data[0]['Ref_data'][required_data]