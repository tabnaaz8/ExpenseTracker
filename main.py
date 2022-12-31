from expense_track import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000, host="0.0.0.0")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
