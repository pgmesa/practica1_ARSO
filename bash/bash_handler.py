import logging

from cli.cli import Cli
from utils.decorators import timer
import bash.commands as repository

# -------------------------------BASH HANDLER-------------------------------
# --------------------------------------------------------------------------
# Defines how the program works and how the command line is going to be read
# and interpreted. The bashCmd module is not coupled with this one, they are
# independent.

commands = {}

@timer
def execute(args:list, flags:list):
    """Executes the commands of the program'"""
    order = args[0]
    command = commands[order]
    args.pop(0)
    command(*args, flg=flags)
        

def config_cli() -> Cli:
    global commands
    cli = Cli()
    # Arguments
    cmd, msg = "crear", ("<void or integer between(1-5)> --> " + 
            " creates and configures the number of servers especified\n " +
            "          (if void, 2 servers are created). It also initializes a load balancer" + 
            " and connects all vms with bridges")
    cli.add_command(cmd, description=msg, extra_arg=True, choices=[1,2,3,4,5], default=2)
    opt, msg = "--name", "<vm_names> allows to specify the name of the vms, 's_' is given if void"
    cli.commands[cmd].add_option(opt, description=msg, extra_arg=True, multi=True, mandatory=True)
    commands[cmd] = repository.crear
    
    cmd, msg = "arrancar", "<void or vm_names> runs the virtual machines specified (stopped or frozen)"
    cli.add_command(cmd, description=msg, extra_arg=True, multi=True)
    commands[cmd] = repository.arrancar
    
    cmd, msg = "parar", "stops the virtual machines currently running"
    cli.add_command(cmd, description=msg, extra_arg=True, multi=True)
    commands[cmd] = repository.parar
    
    cmd, msg = "destruir", "deletes every virtual machine created and all connections betweeen them"
    cli.add_command(cmd, description=msg)
    commands[cmd] = repository.destruir
    
    # Other functionalities
    cmd, msg = "pausar", "pauses the virtual machines currently running"
    cli.add_command(cmd, description=msg, extra_arg=True, multi=True)
    commands[cmd] = repository.pausar
    
    cmd, msg = "lanzar", "executes the create and start commands in a row"
    cli.add_command(cmd, description=msg, extra_arg=True, choices=[1,2,3,4,5], default=2)
    commands[cmd] = repository.lanzar

    cmd, msg = "añadir", "<integer between(1-4)> adds the number of servers specified (the program can't surpass 5 servers)"
    cli.add_command(cmd, description=msg, extra_arg=True, choices=[1,2,3,4], mandatory=True)
    opt, msg = "--name", "<vm_names> allows to specify the name of the vms, 's_' is given if void"
    cli.commands[cmd].add_option(opt, description=msg, extra_arg=True, multi=True, mandatory=True)
    commands[cmd] = repository.añadir
    
    cmd, msg = "eliminar", "<vm_names> deletes the vms specified"
    cli.add_command(cmd, description=msg, extra_arg=True, mandatory=True,  multi=True)
    commands[cmd] = repository.eliminar
    
    cmd, msg = "show", "<diagram or state> shows information about the pupose of the program and it's current state"
    cli.add_command(cmd, description=msg, extra_arg=True, choices=["diagram", "state"], mandatory=True)
    commands[cmd] = repository.show
    
    cmd, msg = "xterm", "<void or vm_name> opens the terminal the vms specified or all of them if no name is given"
    cli.add_command(cmd, description=msg, extra_arg=True, multi=True)
    commands[cmd] = repository.xterm
    
    #Flags/Options
    msg = "shows information about every process that is being executed"
    cli.add_flag("-v", notCompatibleWithFlags=["-d"], description=msg)
    msg = "option for debugging"
    cli.add_flag("-d", notCompatibleWithFlags=["-v"], description=msg)
    msg = "'quiet mode', doesn't show any msg during execution (only when an error occurs)"
    cli.add_flag("-q", notCompatibleWithFlags=["-v","-d"], description=msg)
    msg = "executes the action without asking confirmation"
    cli.add_flag("-f", description=msg)
    msg = "opens the terminal window of the vms that are being started"
    cli.add_flag("-t", description=msg)
    msg = "launches the vm"
    cli.add_flag("-l", description=msg)
    return cli


def config_verbosity(flags:list):
    if "-d" in flags:
        logLvl = logging.DEBUG
        flags.remove("-d")
    elif "-v" in flags:
        logLvl = logging.INFO
        flags.remove("-v")
    elif "-q" in flags:
        logLvl = logging.ERROR
        flags.remove("-q")
    else:
        logLvl = logging.WARNING
    root_logger = logging.getLogger()
    root_logger.setLevel(logLvl) 