import xml.etree.ElementTree as ET
import argparse


def create_column(name, value=None, valueComputed=None):
    if value is not None:
        column = ET.Element("column", name=name, value=value)
    elif valueComputed is not None:
        column = ET.Element("column", name=name, valueComputed=valueComputed)
    else:
        raise ValueError("Either 'value' or 'valueComputed' must be provided.")
    return column


def create_change_set(root, change_set_id, author, dbms):
    change_set = ET.SubElement(root, "changeSet", id=change_set_id, author=author, dbms=dbms)
    return change_set


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Liquibase XML for roles and rights.')
    parser.add_argument('--dbDriver', required=True, help='Database driver (e.g., postgresql)')
    parser.add_argument('--roleName', required=True, help='Role name (e.g., NoViewDeclarationUser)')
    parser.add_argument('--rightsFile', required=True, help='Rights (e.g., T001,T002,T004)')
    parser.add_argument('--revision', required=False, help='Revision (e.g., 1.10.17-1.0.0.1)')

    args = parser.parse_args()

    # Define common attributes as constants
    NAMESPACES = {
        "xmlns": "http://www.liquibase.org/xml/ns/dbchangelog",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation": "http://www.liquibase.org/xml/ns/dbchangelog http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.1.xsd",
        "objectQuotingStrategy": "QUOTE_ONLY_RESERVED_WORDS",
    }

    # Create the root element with common attributes
    root = ET.Element("databaseChangeLog", attrib=NAMESPACES)
    changeset = args.revision + "-" + "add-new-rollback-tag"

    # Tag databaseChangeLog with the revision
    tag_database_changeset = create_change_set(root, changeset, "bob", args.dbDriver)
    rollbackTag = args.revision + "-" + "add-rollback-tag"
    tag_database_changeset.append(ET.Element("tagDatabase", tag=rollbackTag))
    print("Tagged databaseChangeLog with " + rollbackTag)
    ET.Comment("").tail = "\n"

    # Create the role change set
    changeset = args.revision + "-" + "1"
    role_create_change_set = create_change_set(root, changeset, "bob", args.dbDriver)
    role_values = {"role_name": args.roleName, "internal": "true"}
    roleInsetStatement = ET.SubElement(role_create_change_set, "insert", tableName="br_roles", catalogName="public", schemaName="public")
    for key, value in role_values.items():
        roleInsetStatement.append(create_column(key, value=value))
    print("Created role " + args.roleName)
    ET.Comment("").tail = "\n"


    # Create the rights change set
    changeset = args.revision + "-" + "2"
    rights_create_change_set = create_change_set(root, changeset, "bob", args.dbDriver)
    with open(args.rightsFile, 'r') as file:
        rights = [right.strip() for right in file.read().split(' ')]

    for right in rights:
        rightInsertStatement = ET.SubElement(rights_create_change_set, "insert", tableName="br_rights", catalogName="public", schemaName="public")
        rightInsertStatement.append(create_column("rights_type", value=right))
        rightInsertStatement.append(create_column("valid_from", value="1900-01-21"))
        rightInsertStatement.append(create_column("roleId",
                                                  valueComputed="(select id FROM br_roles WHERE role_name = '" + args.roleName + "')"))
        rights_create_change_set.append(rightInsertStatement)
        ET.Comment("").tail = "\n"

    print("Created rights for " + args.roleName)

    # Write the XML to a file
    with open("output.xml", "wb") as file:
        tree = ET.ElementTree(root)
        tree.write(file, encoding='utf-8', xml_declaration=True)
    print("Wrote output to output.xml")
