import subprocess


class Bridge:
    """Clase envoltorio que permite controlar un bridge de lxc

        Args:
            name (str): Nombre del Bridge
            ethernet (str): Nombre del ethernet que le va a asociar lxc
            ipv4_nat (bool, optional): Indica si va a tener ipv4
            ipv4_addr (str, optional): Especifica la ipv4 que va a 
                tener el bridge y el identificador de red que van a 
                tener las ips de los contenedores que se conecten al el
            ipv6_nat (bool, optional): Indica si va a tener ipv6
            ipv6_addr (str, optional): Especifica la ipv6 que va a 
                tener el bridge y el identificador de red que van a 
                tener las ips de los contenedores que se conecten al el
        """
    def __init__(self, name:str, ethernet:str,
                 ipv4_nat:bool=False, ipv4_addr:str=None,
                 ipv6_nat:bool=False, ipv6_addr:str=None):
        self.name = str(name)
        self.is_default = True if self.name == "lxdbr0" else False
        self.ipv4_nat = "true" if ipv4_nat == True else "false"
        self.ipv4_addr = ipv4_addr if ipv4_addr != None else "none"
        self.ipv6_nat = "true" if ipv6_nat == True else "false"
        self.ipv6_addr = ipv6_addr if ipv6_addr != None else "none"
        # El ethernet depende de que bridge se ha creado primero
        # no depende del nombre ni la ip. Lxc asocia una ethernet 
        # al bridge al crearse. Si se ha creado el segundo, lxc le 
        # asociara la eth1 
        self.ethernet = ethernet
        self.used_by = []
    
    def run(self, cmd:list):
        """Ejecuta un comando mediante subprocess y controla los 
        errores que puedan surgir. Espera a que termine el proceso
        (Llamada bloqueante)

        Args:
            cmd (list): Comando a ejecutar

        Raises:
            LxcError: Si surge algun error ejecutando el comando
        """
        process = subprocess.run(
            cmd, 
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE # Para que no salga en consola
        )
        outcome = process.returncode
        if outcome != 0:
            err_msg = (f" Fallo al ejecutar el comando {cmd}.\n" +
                            "Mensaje de error de lxc: ->")
            err_msg += process.stderr.decode().strip()[6:]
            raise LxcNetworkError(err_msg)
  
    def add_container(self, cs_name:str):
        """Añade un contenedor a la red del bridge

        Args:
            cs_name (str): Nombre del contenedor a añadir
        """
        cmd = [
            "lxc", "network", "attach" ,
            self.name, cs_name, self.ethernet
        ]
        self.run(cmd)
        self.used_by.append(cs_name)
    
    def create(self):
        """Crea y configura el bridge. Si el bridge es el default
        (lxdbr0) no se crea puesto que este ya viene creado por
        defecto 'lxc init --auto'"""
        if not self.is_default:
            cmd = ["lxc", "network", "create", self.name]
            self.run(cmd)   
        _set = ["lxc", "network", "set", self.name] 
        self.run(_set + ["ipv4.nat", self.ipv4_nat])
        self.run(_set + ["ipv4.address", self.ipv4_addr])
        self.run(_set + ["ipv6.nat", self.ipv6_nat])
        self.run(_set + ["ipv6.address", self.ipv6_addr])
    
    def delete(self):
        """Elimina el bridge

        Raises:
            LxcNetworkError: Si el bridge esta siendo usado por
                algun contenedor
        """
        if len(self.used_by) == 0:
            if not self.is_default:
                cmd = ["lxc", "network", "delete", self.name]
                self.run(cmd)
            else:
                _set = ["lxc", "network", "set", self.name]
                self.run(_set + ["ipv4.nat", "false"])
                self.run(_set + ["ipv4.address", "none"])
        else:
            err = (f" El bridge '{self.name}' esta siendo usado " +
                  f"por: {self.used_by} y no se puede eliminar")
            raise LxcNetworkError(err)
        
    def __str__(self):
        return self.name

# --------------------------------------------------------------------
class LxcNetworkError(Exception):
    """Excepcion personalizada para los errores al manipular 
    bridges de lxc"""
    pass
# --------------------------------------------------------------------