# phyton.Academia.py
import sqlite3
from datetime import datetime

class GestorEscuela:
    def __init__(self):
        # Inicializamos la conexión a la base de datos
        self.conn = sqlite3.connect('escuela.db')
        self.cursor = self.conn.cursor()
        self.crear_tablas()

    def crear_tablas(self):
        # Creamos la tabla de alumnos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Alumnos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                documento TEXT UNIQUE NOT NULL,
                fecha_nacimiento DATE NOT NULL,
                edad INTEGER NOT NULL,
                curso_id INTEGER,
                FOREIGN KEY (curso_id) REFERENCES Cursos(id)
            )
        ''')

        # Creamos la tabla de docentes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Docentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                documento TEXT UNIQUE NOT NULL,
                fecha_nacimiento DATE NOT NULL,
                edad INTEGER NOT NULL
            )
        ''')

        # Creamos la tabla de cursos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Cursos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                docente_id INTEGER,
                FOREIGN KEY (docente_id) REFERENCES Docentes(id)
            )
        ''')

        self.conn.commit()

    def calcular_edad(self, fecha_nacimiento):
        # fecha_nacimiento es una cadena con formato 'YYYY-MM-DD'
        nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
        hoy = datetime.today()
        edad = hoy.year - nacimiento.year
        if hoy.month < nacimiento.month or (hoy.month == nacimiento.month and hoy.day < nacimiento.day):
            edad -= 1
        return edad
    
    def validar_documento(self, documento):
        # validacion comprobar si solo contiene números
            if not documento.isdigit():
                print("Error: El documento debe contener solo números.")
                return False
            
        # Verifica si el documento tiene 7 o 8 caracteres
            if len(documento) != 7 and len(documento) != 8:
                print("Error: El documento debe tener 7 o 8 caracteres.")
                return False
            return True
    


    def agregar_alumno(self, nombre, apellido, documento, fecha_nacimiento, curso_id):
        try:
            # Validamos que los campos no estén vacíos
            if not nombre or not apellido:
                print("Error: El nombre y el apellido son obligatorios.")
                return None

            # Validamos el documento
            if not self.validar_documento(documento):
                return None

            # Comprobamos si el documento ya existe en la base de datos
            self.cursor.execute("SELECT COUNT(*) FROM Alumnos WHERE documento = ?", (documento,))
            if self.cursor.fetchone()[0] > 0:
                print("Error: El documento del alumno ya existe en la base de datos")
                return None

            # Validamos que la fecha de nacimiento sea válida
            try:
                datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
            except ValueError:
                print("Error: La fecha de nacimiento debe estar en el formato YYYY-MM-DD.")
                return None

            # Calculamos la edad
            edad = self.calcular_edad(fecha_nacimiento)
            if edad < 0:
                print("Error: La fecha de nacimiento no puede ser en el futuro.")
                return None

            # Validamos que el curso_id sea un valor válido
            if not isinstance(curso_id, int) or curso_id <= 0:
                print("Error: El ID del curso debe ser un número entero positivo.")
                return None

            # Insertamos en la tabla Alumnos
            self.cursor.execute('''
                INSERT INTO Alumnos (nombre, apellido, documento, fecha_nacimiento, edad, curso_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (nombre, apellido, documento, fecha_nacimiento, edad, curso_id))

            # Obtenemos el ID del alumno recién insertado
            alumno_id = self.cursor.lastrowid

            self.conn.commit()
            return alumno_id

        except sqlite3.IntegrityError:
            print("Error: El documento del alumno ya existe en la base de datos")
            return None

    def agregar_docente(self, nombre, apellido, documento, fecha_nacimiento):
        try:
            # Validamos que los campos no estén vacíos
            if not nombre or not apellido:
                print("Error: El nombre y el apellido son obligatorios.")
                return None

            # Validamos el documento
            if not self.validar_documento(documento):
                return None

            # Comprobamos si el documento ya existe en la base de datos
            self.cursor.execute("SELECT COUNT(*) FROM Docentes WHERE documento = ?", (documento,))
            if self.cursor.fetchone()[0] > 0:
                print("Error: El documento del docente ya existe en la base de datos")
                return None

            # Validamos que la fecha de nacimiento sea válida
            try:
                datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
            except ValueError:
                print("Error: La fecha de nacimiento debe estar en el formato YYYY-MM-DD.")
                return None

            # Calculamos la edad
            edad = self.calcular_edad(fecha_nacimiento)
            if edad < 0:
                print("Error: La fecha de nacimiento no puede ser en el futuro.")
                return None

            # Insertamos en la tabla Docentes
            self.cursor.execute('''
                INSERT INTO Docentes (nombre, apellido, documento, fecha_nacimiento, edad)
                VALUES (?, ?, ?, ?, ?)
            ''', (nombre, apellido, documento, fecha_nacimiento, edad))

            # Obtenemos el ID del docente recién insertado
            docente_id = self.cursor.lastrowid

            self.conn.commit()
            return docente_id

        except sqlite3.IntegrityError:
            print("Error: El documento del docente ya existe en la base de datos")
        return None

    def agregar_curso(self, nombre, docente_id):
        try:
            # Insertamos en la tabla cursos
            self.cursor.execute('''
                INSERT INTO Cursos (nombre, docente_id)
                VALUES (?, ?)
            ''', (nombre, docente_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error al agregar curso: {e}")
            return False

    def buscar_alumno(self, documento):
        # Buscamos al alumno por documento y mostramos sus detalles junto con su curso
        self.cursor.execute('''
            SELECT a.*, c.nombre AS curso
            FROM Alumnos a
            LEFT JOIN Cursos c ON a.curso_id = c.id
            WHERE a.documento = ?
        ''', (documento,))
        return self.cursor.fetchone() # Usamos fetchone() para obtener la primera fila que coincida

    def buscar_docente(self, documento):
        # Buscamos al docente por documento y mostramos sus detalles
        self.cursor.execute('''
            SELECT * FROM Docentes
            WHERE documento = ?
        ''', (documento,))
        return self.cursor.fetchone()

    def buscar_curso(self, nombre):
        # Buscamos el curso por nombre y mostramos su docente
        self.cursor.execute('''
            SELECT c.*, d.nombre AS docente
            FROM Cursos c
            LEFT JOIN Docentes d ON c.docente_id = d.id
            WHERE c.nombre = ?
        ''', (nombre,))
        return self.cursor.fetchone()

    def actualizar_alumno(self, documento, nombre=None, apellido=None, fecha_nacimiento=None, curso_id=None):
        try:
            # Primero obtenemos el ID del alumno
            self.cursor.execute('SELECT id FROM Alumnos WHERE documento = ?', (documento,))
            alumno = self.cursor.fetchone()
            
            if alumno:
                alumno_id = alumno[0]
            # Validamos que la fecha de nacimiento no sea futura
            if fecha_nacimiento:
                try:
                    # Convertimos la fecha a un objeto datetime
                    fecha_nacimiento_obj = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
                    # Comprobamos si la fecha de nacimiento es futura
                    if fecha_nacimiento_obj > datetime.today():
                        print("Error: La fecha de nacimiento no puede ser en el futuro.")
                        return False
                except ValueError:
                    print("Error: La fecha de nacimiento debe estar en el formato YYYY-MM-DD.")
                    return False    
                # A
                update_fields = []
                update_values = []
                
                if nombre:
                    update_fields.append('nombre = ?')
                    update_values.append(nombre)
                if apellido:
                    update_fields.append('apellido = ?')
                    update_values.append(apellido)
                
                if curso_id:
                    update_fields.append('curso_id = ?')
                    update_values.append(curso_id)
                
                if update_fields:
                    query = f'''UPDATE Alumnos 
                              SET {', '.join(update_fields)}
                              WHERE id = ?'''
                    update_values.append(alumno_id)
                    self.cursor.execute(query, tuple(update_values))

                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Error al actualizar alumno: {e}")
            return False

    def eliminar_alumno(self, documento):
        try:
            # Primero obtenemos el ID del alumno
            self.cursor.execute('SELECT id FROM Alumnos WHERE documento = ?', (documento,))
            alumno = self.cursor.fetchone()
            
            if alumno:
                alumno_id = alumno[0]
                
                # Eliminamos el registro del alumno
                self.cursor.execute('DELETE FROM Alumnos WHERE id = ?', (alumno_id,))
                
                self.conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Error al eliminar alumno: {e}")
            return False

    def listar_alumnos(self):
        # Listamos todos los alumnos
        self.cursor.execute('''
            SELECT a.*, c.nombre AS curso
            FROM Alumnos a
            LEFT JOIN Cursos c ON a.curso_id = c.id
            ORDER BY a.apellido, a.nombre
        ''')
        return self.cursor.fetchall()

    def listar_docentes(self):
        # Listamos todos los docentes
        self.cursor.execute('''
            SELECT * FROM Docentes
            ORDER BY apellido, nombre
        ''')
        return self.cursor.fetchall()

    def listar_cursos(self):
        # Listamos todos los cursos
        self.cursor.execute('''
            SELECT c.*, d.nombre AS docente
            FROM Cursos c
            LEFT JOIN Docentes d ON c.docente_id = d.id
        ''')
        return self.cursor.fetchall()

    def calcular_edad(self, fecha_nacimiento):
        # Calcula la edad de una persona a partir de su fecha de nacimiento
        today = datetime.now().date()
        nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
        edad = today.year - nacimiento.year - ((today.month, today.day) < (nacimiento.month, nacimiento.day))
        return edad

    def __del__(self):
        # Cerramos la conexión al finalizar
        self.conn.close()


def main():
    gestor = GestorEscuela()
    
    while True:
        print("\n╔══════════════════════════════════════════════╗")
        print("║        SISTEMA DE GESTIÓN ESCOLAR           ║")
        print("╚══════════════════════════════════════════════╝\n")
        print("1. AGREGAR ALUMNO  2. AGREGAR DOCENTE  3. AGREGAR CURSO")
        print("4. BUSCAR ALUMNO   5. BUSCAR DOCENTE   6. BUSCAR CURSO")
        print("7. LISTAR ALUMNOS  8. LISTAR DOCENTES  9. LISTAR CURSOS")
        print("10. ACTUALIZAR ALUMNO  11. ELIMINAR ALUMNO")
        print("\n☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆")
        print("                12. SALIR                        ")
        print("☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆☆\n")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            nombre = input("Nombre del alumno: ")
            apellido = input("Apellido del alumno: ")
            documento = input("Documento del alumno: ")
            fecha_nacimiento = input("Fecha de nacimiento (YYYY-MM-DD): ")
            curso_id = input("ID del curso: ")
            gestor.agregar_alumno(nombre, apellido, documento, fecha_nacimiento, int(curso_id))
        
        elif opcion == "2":
            nombre = input("Nombre del docente: ")
            apellido = input("Apellido del docente: ")
            documento = input("Documento del docente: ")
            fecha_nacimiento = input("Fecha de nacimiento (YYYY-MM-DD): ")
            gestor.agregar_docente(nombre, apellido, documento, fecha_nacimiento)
        
        elif opcion == "3":
            nombre = input("Nombre del curso: ")
            docente_id = input("ID del docente: ")
            gestor.agregar_curso(nombre, int(docente_id))
        
        elif opcion == "4":
            documento = input("Documento del alumno: ")
            alumno = gestor.buscar_alumno(documento)
            if alumno:
                print(alumno)
            else:
                print("Alumno no encontrado.")
        
        elif opcion == "5":
            documento = input("Documento del docente: ")
            docente = gestor.buscar_docente(documento)
            if docente:
                print(docente)
            else:
                print("Docente no encontrado.")
        
        elif opcion == "6":
            nombre = input("Nombre del curso: ")
            curso = gestor.buscar_curso(nombre)
            if curso:
                print(curso)
            else:
                print("Curso no encontrado.")
        
        elif opcion == "7":
            alumnos = gestor.listar_alumnos()
            for alumno in alumnos:
                print(alumno)
        
        elif opcion == "8":
            docentes = gestor.listar_docentes()
            for docente in docentes:
                print(docente)
        
        elif opcion == "9":
            cursos = gestor.listar_cursos()
            for curso in cursos:
                print(curso)
        
        elif opcion == "10":
            # Actualizar alumno
            documento = input("Ingrese el documento del alumno a actualizar: ")
            alumno = gestor.buscar_alumno(documento)
            if alumno:
                print("Alumno encontrado. Puede actualizar los siguientes campos:\n")
                print("1. Nombre")
                print("2. Apellido")
                print("3. Fecha de nacimiento")
                print("4. Curso")
                print("5. Ninguno (salir)")
                
                # Seleccionamos qué campos actualizar
                campo_a_actualizar = input("¿Qué desea actualizar? (Ingrese el número): ")
                
                nombre = None
                apellido = None
                fecha_nacimiento = None
                curso_id = None
                
                if campo_a_actualizar == "1":
                    nombre = input("Nuevo nombre: ")
                elif campo_a_actualizar == "2":
                    apellido = input("Nuevo apellido: ")
                elif campo_a_actualizar == "3":
                    fecha_nacimiento = input("Nueva fecha de nacimiento (YYYY-MM-DD): ")
                elif campo_a_actualizar == "4":
                    curso_id = input("Nuevo ID de curso: ")
                
                if gestor.actualizar_alumno(documento, nombre, apellido, fecha_nacimiento, curso_id):
                    print("Alumno actualizado correctamente.")
                else:
                    print("No se pudo actualizar el alumno.")
            else:
                print("Alumno no encontrado.")
        
        elif opcion == "11":
            # Eliminar alumno
            documento = input("Ingrese el documento del alumno a eliminar: ")
            if gestor.eliminar_alumno(documento):
                print("Alumno eliminado correctamente.")
            else:
                print("No se pudo eliminar el alumno o el alumno no existe.")
        
        elif opcion == "12":
            print("Saliendo...")

            break

if __name__ == "__main__":
    main()

