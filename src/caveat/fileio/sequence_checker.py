# Copyright (C) 2025 ERAS Research Group and sanimut Development Team
# Author(s): Torsten Reuschel

#FIXME: this file is a stub


class SequenceChecker():
    """Sequence-aware checker
    """
    def __init__(self, parsers:list = []):
        self.parsers = parsers
        #log # FIXME: use cocotb.logging instead?
        self.log = []
        #initialize empty workspace for parser helper variables and states,
        #e.g. previous' command execution time
        self.system_state = {}

    def append_parser(self, parser:callable):
        """Append parser to list of registered parsers
        """
        self.parsers.append(parser)

    def delete_parser(self, parser_index:int):
        """Delete parser at position 'parser_index' from list of registered
        parsers
        """
        self.parsers.pop(parser_index)

    def get_registered_parser_names(self) -> list:
        """Returns an ordered list of registered parsers
        """
        res = []
        for parser in self.parsers:
            res.append(getattr(parser, '__name__', 'Unknown'))
        return res

    def verify(self, command:any):
        """Apply all parsers in registered sequence to given command object
        """
        command_string = getattr(command, '__name__', 'Unknown')
        for parser in self.parsers:
            parser_name = getattr(parser, '__name__', 'Unknown')
            try:
                self.log.append("{:s}({:s})".format(
                    parser_name,
                    command_string))
                parser(self, command)
            except Exception as e:
                self.log("Error in {:s}: {:s}".format(
                    parser_name,
                    str(e)))
