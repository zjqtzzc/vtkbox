import numpy
from typing import overload

from urdf_parser_py.urdf import Robot as URobot, Joint as UJoint, Link as ULink

from .actor_from_visual import ActorCreator
from .vjoint import VLink, VJoint
from .robot_axes import RobotAxes


class VRobot:
    name: str
    link_map: dict[str, VLink]
    joint_map: dict[str, VJoint]
    root: VLink

    def __init__(self, urdf_path: str, mesh_root_path: str):
        urdf: URobot = URobot.from_xml_file(urdf_path)

        self.name = urdf.name
        self.link_map = {}
        self.joint_map = {}
        self._mimic_map = {}  # type: dict[str, list[str]] # mimiced -> mimicing

        self.positive_joints = []  # type: list[str]

        # register materials
        actor_creator = ActorCreator(mesh_root_path)
        actor_creator.register_material(urdf.materials)

        # create links
        for ulink in urdf.links:
            ulink: ULink
            visual_actors = []
            collision_actors = []
            for visual in ulink.visuals:
                actor = actor_creator.paser_visual(visual)
                if actor:
                    visual_actors.append(actor)
            for collision in ulink.collisions:
                actor = actor_creator.paser_collision(collision)
                if actor:
                    collision_actors.append(actor)
            link = VLink(ulink.name, visual_actors, collision_actors)
            self.link_map[link.name] = link

        # create joints
        for ujoint in urdf.joints:
            joint = VJoint()
            joint.set_input(ujoint)
            self.joint_map[joint.name] = joint

        # check mimic
        for joint in self.joint_map.values():
            if joint.mimic:
                self._mimic_map.setdefault(joint.mimic.joint, []).append(joint.name)

        # check positive
        for joint in self.joint_map.values():
            if joint.type not in ['fixed'] and joint.mimic is None:
                self.positive_joints.append(joint.name)

        # set parent & child
        for joint in self.joint_map.values():
            p_link = self.link_map.get(joint.parent)
            c_link = self.link_map.get(joint.child)
            assert p_link is not None, f'Parent link: {joint.parent} of joint {joint.name} not found'
            assert c_link is not None, f'Child link: {joint.child} of joint {joint.name} not found'
            p_link.children.append(joint.name)
            c_link.parent = joint.name
            p_link.prop.AddPart(joint.prop)
            joint.prop.AddPart(c_link.prop)

        # find root
        root_link = None
        for link in self.link_map.values():
            if not link.parent:
                root_link = link
                break
        assert root_link is not None, 'Root link not found'
        self.root = root_link

        # add axes
        self.axes = RobotAxes(self.link_map)

    def _update(self, j_name: str, pos: float):
        joint = self.joint_map.get(j_name)
        if joint is None:
            print(f'Joint {j_name} not found')
            return
        joint.update(pos)

        if j_name in self._mimic_map:
            for mimic in self._mimic_map[j_name]:
                mimicking_joint = self.joint_map.get(mimic)
                mimicking_joint.update_mimic(pos)

    def set_q(self, q: numpy.ndarray):
        for name, pos in zip(self.positive_joints, q):
            self._update(name, pos)

    def set_joint_pos(self, joint_name: str, pos: float):
        self._update(joint_name, pos)

    def set_joints_pos(self, names: list[str], pos_seq):
        for name, pos in zip(names, pos_seq):
            self._update(name, pos)
