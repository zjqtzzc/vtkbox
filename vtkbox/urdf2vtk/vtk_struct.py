import numpy

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
            ujoint: UJoint
            joint = VJoint(
                ujoint.name, ujoint.type, ujoint.parent, ujoint.child,
                ujoint.origin.xyz, ujoint.origin.rpy, ujoint.axis
            )
            self.joint_map[joint.name] = joint

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

    def move_joint(self, joint_name: str, pos: float):
        joint = self.joint_map.get(joint_name)
        if joint is None:
            raise ValueError(f'Joint {joint_name} not found')
        if joint.type == 'prismatic':
            vector = joint.axis * pos
            joint.prop.SetPosition(vector)
        else:
            vector = joint.axis * numpy.rad2deg(pos)
            joint.prop.SetOrientation(vector)
