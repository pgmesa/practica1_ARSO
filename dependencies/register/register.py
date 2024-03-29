
import os
import pickle
from contextlib import suppress

# --------------------------- REGISTER  ------------------------------
# --------------------------------------------------------------------
# Modulo que proporciona funciones para almacenar objetos en forma
# binaria. Se crea un fichero registro el cual contiene un diccionario
# con tantas paginas como informacion se quiera guardar. En cada 
# pagina, identificada con una clave (register_id) se encuentra la
# informacion relacionada que se quiera guardar junta (una lista con 
# objetos, otro diccionario u objetos o valores aislados). Es una 
# forma de centralizar y facilitar la serializacion de objetos 
# (guardar objetos de forma binaria y ordenada en un mismo fichero)
# --------------------------------------------------------------------

# Ubicacion relativa del registro        
REL_PATH = ".register"
# -------------------------------------------------------------------- 
def config_location(path, name=".register"):
    """Permite configurar la ubicacion del registro y su nombre. 
    Por defecto se crea en la carpeta principal del proyecto

    Args:
        path ([type]): Ubicacion de la carpeta donde se quiere guardar
        name (str, optional): Nombre del registro
    """
    global REL_PATH
    REL_PATH = path+name

# --------------------------------------------------------------------    
def add(register_id:any, obj:object):
    """Crea una nueva pagina del registro. Si el registro no existe
    lo crea

    Args:
        register_id (any): Clave con la que se identifica a la pagina
        obj (object): Variable que se quiere almacenar

    Raises:
        RegisterError: [description]
    """
    if not os.path.exists(REL_PATH):
        register = {}
    else:
        register = load()
    
    if register_id in register:
        raise RegisterError(" id -> '{}' is already used in the register")
    else:
        register[register_id] = obj
        
    with open(REL_PATH, "wb") as file:
            pickle.dump(register, file)

# -------------------------------------------------------------------- 
def update(register_id:any, obj:object, override:bool=True, dict_id:any=None):
    """Acualiza una pagina del registro

    Args:
        register_id (any): Clave que identifica a la pagina
        obj (object): Objeto que se quiere almacenar 
        override (bool, optional): Sobreescribe lo que hubiera
            guardado anteriormente
        dict_id (any, optional): Sirve para indicar, en caso de que 
            override=False y en la pagina del registro hubiera
            almacenado un diccionario, la clave para guardar dentro
            el objeto

    Raises:
        RegisterError: Si la pagina no existe en el registro o hay
            algun fallo al añadir el objeto a la pagina
    """
    register = load()
    if register == None or register_id not in register:
        err_msg = f" id -> '{register_id}' was not found in the register"
        raise RegisterError(err_msg)
    if override == True:
        register[register_id] = obj
    else:
        value_saved = register[register_id]
        if type(value_saved) == list:
            value_saved.append(obj)
        elif type(value_saved) == set:
            value_saved.add(obj)
        elif type(value_saved) == dict:
            if dict_id != None:
                value_saved[dict_id] = obj
            else:
                err_msg = (
                    " A key is needed ('dict_id' property) for updating " + 
                        "(without overriding) the dictionary saved in the " + 
                            f"register with id '{register_id}'"
                )
                raise RegisterError(err_msg)
        elif type(value_saved) == tuple:
            err_msg = (
                    " A tuple object needs to be override it " + 
                    f"(change 'override' property)"
                )
            raise RegisterError(err_msg)
        else:
            array = [value_saved, obj]
            register[register_id] = array
    with open(REL_PATH, "wb") as file:
        pickle.dump(register, file)   

# --------------------------------------------------------------------     
def load(register_id:any=None) -> object:
    """Devuelve la informacion guardada en una pagina del registro.
    Si no se especifica ninguna se devuelve todo el registro

    Args:
        register_id (any, optional): clave de la pagina a recuperar

    Returns:
        object: Devuelve el objeto almacenado en la pagina (pueden
        ser tambien iterables)
    """
    try:
        with open(REL_PATH, "rb") as file:
            register = pickle.load(file)
        if register_id == None:
            return register
        else:
            if register_id in register:
                return register[register_id]
            else:
                return None
    except FileNotFoundError:
        return None

# -------------------------------------------------------------------- 
def override(register:dict):
    """Sobreescribe el registro con un registro nuevo

    Args:
        register (dict): Registro nuevo
    """
    with open(REL_PATH, "wb") as file:
        pickle.dump(register, file)

# --------------------------------------------------------------------    
def remove(register_id:any=None):
    """Elimina una pagina del registro. Si no se especifica ninguna
    se elimina todo el registro

    Args:
        register_id (any, optional): Pagina del registro a eliminar

    Raises:
        RegisterError: Si la pagina especificada no existe
    """
    if register_id != None:
        register = load()
        if register_id in register:
            register.pop(register_id)
            if len(register) == 0:
                os.remove(REL_PATH)
            else:
                override(register)
        else:
            raise RegisterError(f" id '{register_id}' was not found")
    else:
        if os.path.exists(REL_PATH): 
            os.remove(REL_PATH)

# -------------------------------------------------------------------- 
class RegisterError(Exception):
    """Error personalizado para los fallos del registro"""
    def __init__(self, msg):
        super().__init__(msg)

# -------------------------------------------------------------------- 
