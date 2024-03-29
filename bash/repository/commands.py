
import logging
from contextlib import suppress

from .reused_code import target_containers
import program.controllers.bridges as bridges
import program.controllers.containers as containers
import program.machines as machines
import program.functions as program
import dependencies.register.register as register
from dependencies.utils.tools import objectlist_as_dict
from dependencies.utils.tools import concat_array

# --------------------- REPOSITORIO DE COMANDOS ----------------------
# --------------------------------------------------------------------
# Aqui se definen todas las funciones asociadas a los comandos que 
# tiene el programa. Estas funciones se pueden comunicar entre si 
# mediante variables opcionales adicionales para reutilizar el codigo
# --------------------------------------------------------------------

cmd_logger = logging.getLogger(__name__)
# --------------------------------------------------------------------
@target_containers(cmd_logger)           
def arrancar(*target_cs, options={}, flags=[]):
    """Arranca los contenedores que se enceuntren en target_cs

    Args:
        options (dict, optional): Opciones del comando arrancar
        flags (list, optional): Flags introducidos en el programa
    """
    # Arrancamos los contenedores validos
    msg = f" Arrancando contenedores '{concat_array(target_cs)}'..."
    cmd_logger.info(msg)
    succesful_cs = containers.start(*target_cs)
    if not "-q" in flags:
        program.lxc_list()
    cs_s = concat_array(succesful_cs)
    msg = (f" Los contenedores '{cs_s}' han sido arrancados \n")
    cmd_logger.info(msg)
    # Si nos lo indican, abrimos las terminales de los contenedores 
    # arrancados
    if "-t" in flags and len(succesful_cs) > 0:
        c_names = list(map(lambda c: c.name, target_cs))
        term(*c_names, flags=flags)
        
# --------------------------------------------------------------------
@target_containers(cmd_logger) 
def parar(*target_cs, options={}, flags=[]):
    """Detiene los contenedores que se enceuntren en target_cs

    Args:
        options (dict, optional): Opciones del comando parar
        flags (list, optional): Flags introducidos en el programa
    """
    # Paramos los contenedores validos
    msg = f" Deteniendo contenedores '{concat_array(target_cs)}'..."
    cmd_logger.info(msg)
    succesful_cs = containers.stop(*target_cs)
    if not "-q" in flags:
        program.lxc_list()
    cs_s = concat_array(succesful_cs)
    msg = (f" Los contenedores '{cs_s}' han sido detenidos \n")
    cmd_logger.info(msg)
        
# --------------------------------------------------------------------  
@target_containers(cmd_logger)  
def pausar(*target_cs, options={}, flags=[]):
    """Pausa los contenedores que se enceuntren en target_cs

    Args:
        options (dict, optional): Opciones del comando pausar
        flags (list, optional): Flags introducidos en el programa
    """
    # Pausamos los contenedores validos
    msg = f" Pausando contenedores '{concat_array(target_cs)}'..."
    cmd_logger.info(msg)
    succesful_cs = containers.pause(*target_cs)
    if not "-q" in flags:
        program.lxc_list()
    cs_s = concat_array(succesful_cs)
    msg = (f" Los contenedores '{cs_s}' han sido pausados \n")
    cmd_logger.info(msg)

# --------------------------------------------------------------------
@target_containers(cmd_logger) 
def eliminar(*target_cs, options={}, flags=[],
                    skip_tags=[machines.LB, machines.CLIENT]): 
    """Elimina los contenedores que se enceuntren en target_cs.
    Por defecto, esta funcion solo elimina los contenedores que 
    sean servidores

    Args:
        options (dict, optional): Opciones del comando eliminar
        flags (list, optional): Flags introducidos en el programa
        skip_tags (list, optional): Variable que permite que destruir
            se comunique con esta funcion. Por defecto esta funcion 
            no elimina contenedores que sean clientes o balanceadores
    """
    target_cs = filter(lambda cs: not cs.tag in skip_tags, target_cs)
    target_cs = list(target_cs)
    if len(target_cs) == 0:
        msg = (" No hay servidores que eliminar o los " + 
                                    "introducidos no son validos")
        cmd_logger.error(msg)
        return
    if not "-f" in flags:
        print("Se eliminaran los servidores:" +
                    f" '{concat_array(target_cs)}'")
        answer = str(input("¿Estas seguro?(y/n): "))
        if answer.lower() != "y":
            return
    # Eliminamos los existentes que nos hayan indicado
    msg = f" Eliminando contenedores '{concat_array(target_cs)}'..."
    cmd_logger.info(msg)
    succesful_cs = containers.delete(*target_cs)
    # Actualizamos los contenedores que estan asociados a cada bridge
    program.update_conexions()
    if not "-q" in flags:
        program.lxc_list()
    cs_s = concat_array(succesful_cs)
    msg = (f" Los contenedores '{cs_s}' han sido eliminados \n")
    cmd_logger.info(msg)

# --------------------------------------------------------------------
@target_containers(cmd_logger) 
def term(*target_cs, options={}, flags=[]):
    """Abre la terminal los contenedores que se enceuntren en 
    target_cs

    Args:
        options (dict, optional): Opciones del comando term
        flags (list, optional): Flags introducidos en el programa
    """
    # Arrancamos los contenedores validos
    cs_s = concat_array(target_cs)
    msg = f" Abriendo terminales de contenedores '{cs_s}'..."
    cmd_logger.info(msg)
    succesful_cs = containers.open_terminal(*target_cs)
    cs_s = concat_array(succesful_cs)
    msg = f" Se ha abierto la terminal de los contenedores '{cs_s}'\n"
    cmd_logger.info(msg)
    
    # --------------------------------------------------------------------
def añadir(numServs:int, options={}, flags=[], extra_cs=[]):
    """Añade el numero de contenedores especificados a la plataforma
    de servidores. Por defecto solo añade contenedores que sean del
    tipo servidor, pero en extra_cs se pueden especificar contenedores 
    de cualquier tipo que tambien se quiran añadir

    Args:
        numServs (int): Numero de servidores a añadir
        options (dict, optional): Opciones del comando añadir
        flags (list, optional): Flags introducidos en el programa
        extra_cs (list, optional): Variable utilizada para que 'crear' se
            pueda comunicar con esta funcion y tambien cree los 
            clientes y el balanceador, ademas de los servidores
    """
    if register.load(bridges.ID) == None:
        msg = (" La plataforma de servidores no ha sido " +
                    "desplegada, se debe crear una nueva antes " +
                        "de añadir los servidores")
        cmd_logger.error(msg)
        return
    existent_cs = register.load(containers.ID)
    if existent_cs != None:
        ex_s = filter(lambda cs: cs.tag == machines.SERVER, existent_cs)
        num = len(list(ex_s))
        if num + numServs > 5: 
            msg = (f" La plataforma no admite mas de 5 servidores. " +
                    f"Actualmente existen {num}, no se " +
                            f"puede añadir {numServs} mas")
            cmd_logger.error(msg)
            return
    # Creando contenedores 
        # Elegimos la imagen con la que se van a crear
    simage = machines.default_image
    if "--image" in options:
        simage = options["--image"][0]
    if "--simage" in options:
        simage = options["--simage"][0]
    cmd_logger.debug(f" Creando servidores con imagen '{simage}'")
    if "--name" in options:   
        names = options["--name"]
        cs = extra_cs + machines.get_servers(
            numServs, 
            *names, 
            image=simage
        )
    else:
        cs = extra_cs + machines.get_servers(
            numServs,
            image=simage
        )
    cs_s = concat_array(cs)
    msg = f" Nombre de contenedores serializados --> '{cs_s}'"
    cmd_logger.debug(msg)
    launch = True if "-l" in flags else False
    show = True if not launch and "-q" not in flags else False
    cmd_logger.debug(f" Launch --> {launch} | show --> {show}")
    cmd_logger.info(f" Inicializando contenedores '{cs_s}'...")
    successful_cs = containers.init(*cs)
    if not "-q" in flags:
        program.lxc_list() 
    cs_s = concat_array(successful_cs)
    msg = (f" Contenedores '{cs_s}' inicializados\n")
    cmd_logger.info(msg)
    if len(successful_cs) != 0:     
        # Estableciendo conexiones
        cmd_logger.info(" Estableciendo conexiones " +
                                "entre contenedores y bridges...")
        program.connect_machines()
        cmd_logger.info(" Conexiones establecidas\n")
        # Arrancamos los contenedores creados con exito 
        # (si nos lo han pedido) 
        if successful_cs != None and launch:
            c_names = list(map(lambda c: c.name, successful_cs))
            arrancar(*c_names, flags=flags) 
                 
# --------------------------------------------------------------------
def crear(numServs:int, options={}, flags=[]):
    """Crea la plataforma del sistema-servidor, desplegando los 
    bridges y contenedores y conectandolos entre ellos (de la forma
    que se hayan definido estas conexiones en la carpeta program)

    Args:
        numServs (int): Numero de servidores a crear
        options (dict, optional): Opciones del comando crear
        flags (list, optional): Flags introducidos en el programa
    """
    if register.load(bridges.ID) != None:
        msg = (" La plataforma de servidores ya ha sido desplegada, " 
              + "se debe destruir la anterior para crear otra nueva")
        cmd_logger.error(msg)
        return   
    cmd_logger.info(" Desplegando la plataforma de servidores...\n")
    # Creando bridges
    bgs = machines.get_bridges(numBridges=2)
    bgs_s = concat_array(bgs)
    cmd_logger.debug(f" Nombre de bridges serializado --> '{bgs_s}'")
    cmd_logger.info(" Creando bridges...")
    succesful_bgs = bridges.init(*bgs)
    if not "-q" in flags:
        program.lxc_network_list()
    bgs_s = concat_array(succesful_bgs)
    cmd_logger.info(f" Bridges '{bgs_s}' creados\n")
    # Creando contenedores
        # Elegimos la imagen con la que se van a crear
    lbimage = machines.default_image
    climage = machines.default_image
    if "--image" in options:
        climage = options["--image"][0]
        lbimage = options["--image"][0]
    if "--climage" in options:
        climage = options["--climage"][0]
    if "--lbimage" in options:
        lbimage = options["--lbimage"][0]
    cmd_logger.debug(f" Creando cliente con imagen '{climage}'")
    cmd_logger.debug(f" Creando lb con imagen '{lbimage}'")
    lb = machines.get_loadbalancer(image=lbimage)
    cl = machines.get_clients(image=climage)
    añadir(numServs, options=options, flags=flags, extra_cs=[lb,cl]) 
    cmd_logger.info(" Plataforma de servidores desplegada")

# --------------------------------------------------------------------
def destruir(options={}, flags=[]):
    """Destruye la platafrma del sistema-servidor eliminando todos
    sus componenetes (bridges, contenedores y las conexiones entre
    ellos). Reutiliza el codigo de la funcion eliminar para eliminar
    los contenedores.

    Args:
        options (dict, optional): Opciones del comando destruir
        flags (list, optional): Flags introducidos en el programa
    """
    if not "-f" in flags:
        msg = ("Se borrara por completo la infraestructura " + 
                "creada, contenedores, bridges y sus conexiones " + 
                    "aun podiendo estar arrancadas")
        print(msg)
        answer = str(input("¿Estas seguro?(y/n): "))
        if answer.lower() != "y":
            return
    if register.load(bridges.ID) == None:
        msg = (" La plataforma de servidores no ha sido desplegada, " 
                 + "se debe crear una nueva antes de poder destruir")
        cmd_logger.error(msg)
        return
    cmd_logger.info(" Destruyendo plataforma...\n")
    # Eliminamos contenedores
    cs = register.load(containers.ID)
    if cs == None:
        cmd_logger.warning(" No existen contenedores en el programa\n")
    else:
        c_names = list(map(lambda c: c.name, cs))
        flags.append("-f") # Añadimos el flag -f
        eliminar(*c_names, flags=flags, skip_tags=[])
    # Eliminamos bridges
    bgs = register.load(bridges.ID)
    if bgs == None: 
        cmd_logger.warning(" No existen bridges en el programa")
    else:
        msg = f" Eliminando bridges '{concat_array(bgs)}'..."
        cmd_logger.info(msg)
        successful_bgs = bridges.delete(*bgs)
        if not "-q" in flags:
            program.lxc_network_list()
        bgs_s = concat_array(successful_bgs)
        msg = (f" Bridges '{bgs_s}' eliminados\n")
        cmd_logger.info(msg)  
    # Si se ha elimando todo eliminamos el registro   
    cs = register.load(containers.ID)
    bgs = register.load(bridges.ID) 
    if cs == None and bgs == None:
        register.remove()
        cmd_logger.info(" Plataforma destruida")
    else:
        msg = (" Plataforma destruida parcialmente " +
                        "(se han encontrado dificultades)") 
        cmd_logger.error(msg)
            
# --------------------------------------------------------------------   
def show(choice:str, options={}, flags={}):
    """Muestra informacion sobre el programa

    Args:
        choice (str): Indica que informacion se quiere mostrar
        options (dict, optional): Opciones del comando show
        flags (list, optional): Flags introducidos en el programa
    """
    if choice == "diagram":
        program.show_diagram()
    elif choice == "state":
        program.print_state()
    elif choice == "files":
        program.show_files_structure()
        
# --------------------------------------------------------------------