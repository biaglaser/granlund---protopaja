from website import app_create

app = app_create()

#run app! start listening for post requests from device
if __name__ == '__main__':
    app.run(port=3000, debug=True)

