def handle_uploaded_file(file):
    data = "".join([line.decode("utf-8") for line in file.readlines()])
    return data
