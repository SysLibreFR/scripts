import pyodbc

# Tester la connexion
try:
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=serveurcegidpmi;"
        "DATABASE=PMI;"
        "UID=assurance_import;"
        "PWD=mdp;"
    )
    cursor = conn.cursor()
    
    # Test SELECT
    cursor.execute("SELECT TOP 1 * FROM CLIENT WHERE CLKTSOC = '100'")
    print("✓ SELECT OK")
    
    # Test UPDATE
    cursor.execute("""
        UPDATE CLIENT 
        SET CLCTLIBRE3 = 'Test Python' 
        WHERE CLKTSOC = '100' AND CLKTCODE = '100240'
    """)
    conn.commit()
    print("✓ UPDATE OK")
    
    cursor.close()
    conn.close()
    print("\n✓ Toutes les permissions fonctionnent correctement")
    
except Exception as e:
    print(f"✗ Erreur : {e}")