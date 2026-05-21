from app import create_app

app = create_app()

if __name__ == '__main__':
    # 預設在本機開啟 debug 模式運行
    app.run(debug=True)
