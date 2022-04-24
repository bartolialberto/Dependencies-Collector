from asyncio import InvalidStateError
from entities.enums.TypesRR import TypesRR
from entities.paths.APath import APath
from entities.paths.CNAMEPath import CNAMEPath
from entities.paths.MXPath import MXPath
from entities.paths.NSPath import NSPath
from entities.paths.Path import Path
from entities.RRecord import RRecord
from exceptions.PathIntegrityError import PathIntegrityError


class PathBuilder:
    """
    This class permits to create one step at time every instance of a Path object.

    ...

    Attributes
    ----------
    constructing_path : List[RRecord]
        List of resource records.
    is_resolved : bool
        State of the path that determines if the building process is complete or not.
    """
    def __init__(self):
        """
        Initialize the object.

        """
        self.constructing_path = list()
        self.is_resolved = False

    def complete_resolution(self, rr: RRecord) -> 'PathBuilder':        # FORWARD DECLARATIONS (REFERENCES)
        """
        It completes the path with a final resource record.

        :param rr: A resource record
        :type rr: RRecord
        :raise InvalidStateError: If the constructing path is already completed.
        :raise PathIntegrityError: If the resource record parameter to be added does not comply to a valid Path
        :return: Itself
        :rtype: PathBuilder
        """
        if self.is_resolved:
            raise InvalidStateError
        self.constructing_path.append(rr)
        if Path.check_path_integrity(self.constructing_path):
            self.is_resolved = True
            return self
        else:
            raise PathIntegrityError

    def complete_as_cnamepath(self) -> 'PathBuilder':       # FORWARD DECLARATIONS (REFERENCES)
        """
        It completes the current CNAME chain of resource records as a CNAMEPath.

        :raise InvalidStateError: If the constructing path is already completed.
        :raise IndexError: If the constructing path is empty.
        :return:
        :rtype:
        """
        if self.is_resolved:
            raise InvalidStateError
        try:
            resolution_rr = self.constructing_path.pop()
        except IndexError:
            raise
        return self.complete_resolution(resolution_rr)

    def add_cname(self, rr: RRecord) -> 'PathBuilder':      # FORWARD DECLARATIONS (REFERENCES)
        """
        It added a CNAME resource record before the final resource record.

        :param rr: A resource record
        :type rr: RRecord
        :raise ValueError: If a non-CNAME resource record is appended before the final one.
        :raise InvalidStateError: If the constructing path is already completed.
        :raise PathIntegrityError: If the resource record parameter to be added does not comply to a valid Path
        :return: Itself
        :rtype: PathBuilder
        """
        if self.is_resolved:
            raise InvalidStateError
        if rr.type != TypesRR.CNAME:
            raise ValueError
        else:
            self.constructing_path.append(rr)
        if Path.check_path_integrity(self.constructing_path):
            return self
        else:
            raise PathIntegrityError

    def build(self) -> Path:
        """
        Completes the building process. It translates the completed PathBuilder to an instance of the Path class,
        based on the type of the final resource record (successfully) added.

        :return: The path object
        :rtype: Path
        """
        if self.is_resolved:
            if self.constructing_path[-1].type == TypesRR.A:
                return APath(self.constructing_path)
            elif self.constructing_path[-1].type == TypesRR.MX:
                return MXPath(self.constructing_path)
            elif self.constructing_path[-1].type == TypesRR.NS:
                return NSPath(self.constructing_path)
            else:
                return CNAMEPath(self.constructing_path)
        else:
            raise InvalidStateError

    @staticmethod
    def from_cname_path(cname_path: CNAMEPath) -> 'PathBuilder':       # FORWARD DECLARATIONS (REFERENCES)
        """
        It constructs a PathBuilder object from a CNAMEPath object. This means that the resulting PathBuilder will
        have all the CNAME resource records from the CNAMEPath object in the CNAME chain, but no resolution resource
        record.

        :param cname_path: A CNAMEPath object.
        :type cname_path: CNAMEPath
        :return: The PathBuilder object.
        :rtype: PathBuilder
        """
        a_pb = PathBuilder()
        for rr in cname_path:
            a_pb.add_cname(rr)
        return a_pb
