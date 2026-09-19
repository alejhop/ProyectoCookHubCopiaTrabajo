from controlador.controlador import app

if __name__ == "__main__":
    print("👨‍🍳 CookHub Backend iniciado en http://localhost:5001")
    print("📊 Endpoints disponibles:")
    print("   GET/POST /api/recetas")
    print("   GET/PUT/DELETE /api/recetas/<id>")
    print("   GET/POST /api/ingredientes")
    print("   GET/PUT/DELETE /api/ingredientes/<id>")
    print("   GET /api/reportes/ingredientes")
    app.run(debug=True, port=5001)
