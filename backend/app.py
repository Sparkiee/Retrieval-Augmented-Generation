from flask import Flask, render_template, request, jsonify
from flask_cors import cross_origin
from RAGmodel import QueryParser

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/query", methods=["POST"])
@cross_origin()
def query_model():
    query = request.json.get("query")
    
    print("Query is: ", query)

    parser = QueryParser(query)

    response = parser.process_query()

    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
