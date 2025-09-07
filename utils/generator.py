# utils/generator.py
import numpy as np
import trimesh
import os

class FunkoChibiGenerator:
    def __init__(self):
        self.tolerance = -0.05
        self.scale = 1.0
        self.character_type = "human"
        self.gender = "male"
        self.hair_style = "short"
        self.clothing = "none"

    def set_tolerance(self, tol):
        self.tolerance = tol

    def create_basic_head(self, scale=1.0):
        """Crear cabeza básica estilo chibi"""
        # Esfera como base
        head = trimesh.creation.icosphere(subdivisions=2, radius=0.8 * scale)
        # Aplanar ligeramente
        vertices = head.vertices.copy()
        vertices[:, 1] *= 0.9  # Aplanar en Y
        head.vertices = vertices
        return head

    def create_basic_hair(self, style="short", scale=1.0):
        """Crear cabello básico"""
        if style == "short":
            hair = trimesh.creation.icosphere(subdivisions=2, radius=0.85 * scale)
            # Hacerlo ligeramente más alto
            vertices = hair.vertices.copy()
            vertices[:, 2] += 0.1 * scale  # Subir en Z
            hair.vertices = vertices
        elif style == "long":
            # Cilindro para pelo largo
            hair = trimesh.creation.cylinder(radius=0.7 * scale, height=0.3 * scale, sections=16)
            hair.apply_translation([0, 0, 0.5 * scale])
        else:
            # Sin pelo - malla vacía
            hair = trimesh.Trimesh()
        return hair

    def create_basic_eye(self, side="left", scale=1.0):
        """Crear ojo básico"""
        offset_x = -0.3 * scale if side == "left" else 0.3 * scale
        offset_y = 0.4 * scale
        offset_z = 0.0
        
        # Ojo blanco
        eye_white = trimesh.creation.icosphere(subdivisions=1, radius=0.1 * scale)
        eye_white.apply_translation([offset_x, offset_y, offset_z])
        
        # Pupila
        pupil = trimesh.creation.icosphere(subdivisions=1, radius=0.06 * scale)
        pupil.apply_translation([offset_x, offset_y + 0.02, offset_z])
        
        return eye_white, pupil

    def create_basic_torso(self, scale=1.0):
        """Crear torso básico"""
        torso = trimesh.creation.box(extents=[0.6 * scale, 0.4 * scale, 0.8 * scale])
        torso.apply_translation([0, 0, 1.2 * scale])
        return torso

    def create_basic_arm(self, side="left", scale=1.0):
        """Crear brazo básico"""
        arm = trimesh.creation.cylinder(radius=0.15 * scale, height=1.0 * scale, sections=16)
        if side == "left":
            arm.apply_translation([-0.5 * scale, 0, 1.2 * scale])
        else:
            arm.apply_translation([0.5 * scale, 0, 1.2 * scale])
        # Rotar para que apunte hacia abajo
        rotation_matrix = trimesh.transformations.rotation_matrix(
            np.pi/2, [1, 0, 0])
        arm.apply_transform(rotation_matrix)
        return arm

    def create_basic_leg(self, side="left", scale=1.0):
        """Crear pierna básica"""
        leg = trimesh.creation.cylinder(radius=0.18 * scale, height=1.5 * scale, sections=16)
        if side == "left":
            leg.apply_translation([-0.25 * scale, 0, 0.3 * scale])
        else:
            leg.apply_translation([0.25 * scale, 0, 0.3 * scale])
        # Rotar para que apunte hacia abajo
        rotation_matrix = trimesh.transformations.rotation_matrix(
            np.pi/2, [1, 0, 0])
        leg.apply_transform(rotation_matrix)
        return leg

    def create_basic_hand(self, side="left", scale=1.0):
        """Crear mano básica"""
        hand = trimesh.creation.icosphere(subdivisions=1, radius=0.12 * scale)
        if side == "left":
            hand.apply_translation([-0.5 * scale, 0, 0.2 * scale])
        else:
            hand.apply_translation([0.5 * scale, 0, 0.2 * scale])
        return hand

    def create_basic_foot(self, side="left", scale=1.0):
        """Crear pie básico"""
        foot = trimesh.creation.icosphere(subdivisions=1, radius=0.15 * scale)
        # Hacerlo más ancho
        vertices = foot.vertices.copy()
        vertices[:, 1] *= 1.5  # Ancho en Y
        vertices[:, 2] *= 0.5  # Alto en Z
        foot.vertices = vertices
        
        if side == "left":
            foot.apply_translation([-0.25 * scale, 0, -0.8 * scale])
        else:
            foot.apply_translation([0.25 * scale, 0, -0.8 * scale])
        return foot

    def create_socket(self, location, radius=0.1, depth=0.1, tolerance=-0.05):
        """Crear socket de encastre"""
        socket = trimesh.creation.cylinder(radius=radius - tolerance, height=depth, sections=16)
        socket.apply_translation(location)
        return socket

    def create_insert(self, location, radius=0.1, depth=0.12, tolerance=-0.05):
        """Crear inserto para encajar"""
        insert = trimesh.creation.cylinder(radius=radius + tolerance, height=depth, sections=16)
        insert.apply_translation(location)
        return insert

    def subtract_mesh(self, base_mesh, subtract_mesh):
        """Restar una malla de otra (operación booleana)"""
        try:
            if len(base_mesh.vertices) > 0 and len(subtract_mesh.vertices) > 0:
                result = base_mesh.difference(subtract_mesh, engine='scad')
                return result if result is not None else base_mesh
            return base_mesh
        except:
            return base_mesh

    def generate_full_model(self):
        """Generar modelo completo"""
        parts = {}
        scale = self.scale
        
        # Cabeza
        head = self.create_basic_head(scale)
        parts["head"] = head
        
        # Pelo (si no es calvo)
        if self.hair_style != "bald":
            hair = self.create_basic_hair(self.hair_style, scale)
            # Restar el pelo de la cabeza para crear hueco
            head_with_hair_cut = self.subtract_mesh(head, hair)
            parts["head"] = head_with_hair_cut
            parts["hair"] = hair
        
        # Ojos
        eye_left, pupil_left = self.create_basic_eye("left", scale)
        eye_right, pupil_right = self.create_basic_eye("right", scale)
        parts["eye_left"] = eye_left
        parts["pupil_left"] = pupil_left
        parts["eye_right"] = eye_right
        parts["pupil_right"] = pupil_right
        
        # Torso
        parts["torso"] = self.create_basic_torso(scale)
        
        # Brazos
        parts["arm_left"] = self.create_basic_arm("left", scale)
        parts["arm_right"] = self.create_basic_arm("right", scale)
        
        # Manos
        parts["hand_left"] = self.create_basic_hand("left", scale)
        parts["hand_right"] = self.create_basic_hand("right", scale)
        
        # Piernas
        parts["leg_left"] = self.create_basic_leg("left", scale)
        parts["leg_right"] = self.create_basic_leg("right", scale)
        
        # Pies
        parts["foot_left"] = self.create_basic_foot("left", scale)
        parts["foot_right"] = self.create_basic_foot("right", scale)
        
        # Conectores - Cuello
        neck_location = [0, 0, 1.8 * scale]
        parts["neck_socket"] = self.create_socket(neck_location, 0.1 * scale, 0.1 * scale, self.tolerance)
        parts["neck_insert"] = self.create_insert(neck_location, 0.1 * scale, 0.12 * scale, self.tolerance)
        
        # Conectores - Brazos
        arm_locations = [
            [-0.5 * scale, 0, 1.2 * scale],  # Izquierdo
            [0.5 * scale, 0, 1.2 * scale]    # Derecho
        ]
        for i, loc in enumerate(arm_locations):
            side = "left" if i == 0 else "right"
            parts[f"arm_socket_{side}"] = self.create_socket(loc, 0.1 * scale, 0.1 * scale, self.tolerance)
            parts[f"arm_insert_{side}"] = self.create_insert(loc, 0.1 * scale, 0.12 * scale, self.tolerance)
        
        # Conectores - Piernas
        leg_locations = [
            [-0.25 * scale, 0, 0.3 * scale],  # Izquierda
            [0.25 * scale, 0, 0.3 * scale]    # Derecha
        ]
        for i, loc in enumerate(leg_locations):
            side = "left" if i == 0 else "right"
            parts[f"leg_socket_{side}"] = self.create_socket(loc, 0.1 * scale, 0.1 * scale, self.tolerance)
            parts[f"leg_insert_{side}"] = self.create_insert(loc, 0.1 * scale, 0.12 * scale, self.tolerance)
        
        return parts

    def export_parts(self, output_path, file_format="STL"):
        """Exportar partes a STL u OBJ"""
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
        parts = self.generate_full_model()
        exported_files = []
        
        for name, mesh in parts.items():
            if len(mesh.vertices) == 0:
                continue
                
            filepath = os.path.join(output_path, f"{name}.{file_format.lower()}")
            try:
                if file_format.upper() == "STL":
                    mesh.export(filepath, file_type="stl")
                elif file_format.upper() == "OBJ":
                    mesh.export(filepath, file_type="obj")
                exported_files.append(filepath)
            except Exception as e:
                print(f"Error exporting {name}: {e}")
                
        return exported_files
