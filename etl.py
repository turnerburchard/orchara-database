import os
from extract import extract_file
from transform import transform_item
from load import get_connection, create_table_if_not_exists, insert_item


def process_file(filepath, cur):
    print(f"Processing file: {filepath}")
    items = extract_file(filepath)
    for item in items:
        processed = transform_item(item)
        if processed is None:
            continue
        insert_item(cur, processed)
    cur.connection.commit()
    print(f"Finished processing {filepath}")


def main():
    conn = get_connection()
    cur = conn.cursor()
    create_table_if_not_exists(cur)

    data_folder = 'data'
    # Process each file independently.
    for filename in os.listdir(data_folder):
        if filename.endswith('.json.gz'):
            filepath = os.path.join(data_folder, filename)
            process_file(filepath, cur)

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
