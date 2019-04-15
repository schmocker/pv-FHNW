from pvtool import create_app, Config

if __name__ == "__main__":
    app = create_app(Config)
    app.run(host='0.0.0.0', port=5000, debug=True)
