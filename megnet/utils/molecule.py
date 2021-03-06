import logging

from pymatgen import Molecule
import numpy as np

try:
    import pybel as pb
    import openbabel as ob
except ImportError:
    logging.warning("Openbabel is needed for molecule models, try 'conda install -c openbabel openbabel' to install it")
    pb = None
    ob = None

from typing import List


class MEGNetMolecule(Molecule):
    def get_all_neighbors(self, cutoff: float, include_index: bool = True,
                          include_image: bool = True, **kwargs) -> List[List]:
        """

        Args:
            cutoff: float, cutoff radius
            include_index: bool, whether to include the site index
            include_image: bool, whether to include dummy image

        Returns:
            list of list, neighbors for each site
        """

        dist = self.distance_matrix
        neighbors = []
        for i in dist:
            cond = np.bitwise_and(i <= cutoff, i > 1e-8)
            inds = np.array(np.where(cond)[0], dtype='int')
            d = i[cond]
            images = [(0, 0, 0)] * len(d)
            neighbor = []
            for k, l, m in zip(d, inds, images):
                item = []
                item.append(self[l])
                item.append(k)
                if include_index:
                    item += [l]
                if include_image:
                    item += [m]
                neighbor.append(item)
            neighbors.append(neighbor)
        return neighbors

    @classmethod
    def from_pymatgen(cls, mol: Molecule) -> 'MEGNetMolecule':
        sites = mol._sites
        return cls.from_sites(sites)


def get_pmg_mol_from_smiles(smiles: str) -> Molecule:
    """
    Get a pymatgen molecule from smiles representation
    Args:
        smiles: (str) smiles representation of molecule
    """
    b_mol = pb.readstring('smi', smiles)
    b_mol.make3D()
    b_mol = b_mol.OBMol
    sp = []
    coords = []
    for atom in ob.OBMolAtomIter(b_mol):
        sp.append(atom.GetAtomicNum())
        coords.append([atom.GetX(), atom.GetY(), atom.GetZ()])
    return Molecule(sp, coords)
