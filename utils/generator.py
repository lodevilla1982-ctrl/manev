# utils/generator.py
import numpy as np
import trimesh
import os
from pathlib import Path

class FunkoChibiGenerator:
    def __init__(self):
        self.assets_path = "assets"
        self.tolerance = -0.05
        self.scale = 1.0
        self.gender = "male"
        self.hair_style = "short"
        self.clothing = "none"

    def set_tolerance(self, tol):
        self.tolerance = tol

    def load_model(self, path):
        """Cargar modelo STL desde assets"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Modelo no encontrado: {path}")
        return trimesh.load(path)

    def create_socket(self, location, radius=0.1, depth=0.1, tolerance=-0.05):
        """Crear socket de encastre"""
        socket = trimesh.creation.cylinder(radius=radius - tolerance, height=depth)
        socket.apply_translation(location)
        return socket

    def create_insert(self, location, radius=0.1, depth=0.12, tolerance=-0.05):
        """Crear inserto para encajar"""
        insert = trimesh.creation.cylinder(radius=radius + tolerance, height=depth)
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

    def generate_head_with_hair(self, head_path, hair_path, scale=1.0):
        """Generar cabeza con corte para pelo"""
        # Cargar modelos
        head = self.load_model(head_path)
        hair = self.load_model(hair_path)
        
        # Escalar
        head.apply_scale(scale)
        hair.apply_scale(scale)
        
        # Alinear posiciones
        hair.apply_translation([0, 0, 0.1 * scale])  # Ligeramente arriba
        
        # Cortar hueco en la cabeza para el pelo
        head_with_cut = self.subtract_mesh(head, hair)
        
        return head_with_cut, hair

    def generate_eyes(self, eye_white_path, pupil_path, scale=1.0):
        """Generar ojos con pupila"""
        eye_white = self.load_model(eye_white_path)
        pupil = self.load_model(pupil_path)
        
        # Escalar
        eye_white.apply_scale(scale)
        pupil.apply_scale(scale)
        
        # Posicionar pupila dentro del ojo blanco
        pupil.apply_translation([0, 0, 0.01])
        
        # Cortar hueco en el ojo blanco para la pupila
        eye_with_pupil = self.subtract_mesh(eye_white, pupil)
        
        return eye_with_pupil, pupil

    def generate_full_model(self):
        """Generar modelo completo con todas las partes"""
        parts = {}
        scale = self.scale
        
        # Rutas de modelos
        base_dir = os.path.join(self.assets_path, "heads")
        head_path = os.path.join(base_dir, f"{self.gender}_head.stl")
        hair_dir = os.path.join(self.assets_path, "hair")
        hair_path = os.path.join(hair_dir, f"{self.hair_style}_{self.gender}.stl")
        
        # Cabeza con corte para pelo
        head, hair = self.generate_head_with_hair(head_path, hair_path, scale)
        parts["head"] = head
        parts["hair"] = hair
        
        # Ojos
        eye_white_path = os.path.join(self.assets_path, "eyes", "eye_white.stl")
        pupil_path = os.path.join(self.assets_path, "eyes", "pupil_black.stl")
        eye, pupil = self.generate_eyes(eye_white_path, pupil_path, scale)
        parts["eye"] = eye
        parts["pupil"] = pupil
        
        # Torso
        torso_path = os.path.join(self.assets_path, "body", f"{self.gender}_torso.stl")
        torso = self.load_model(torso_path)
        torso.apply_scale(scale)
        parts["torso"] = torso
        
        # Brazos
        arm_path = os.path.join(self.assets_path, "arms", "arm_left.stl")
        arm = self.load_model(arm_path)
        arm.apply_scale(scale)
        parts["arm"] = arm
        
        # Piernas
        leg_path = os.path.join(self.assets_path, "legs", "leg_left.stl")
        leg = self.load_model(leg_path)
        leg.apply_scale(scale)
        parts["leg"] = leg
        
        # Conectores
        neck_location = [0, 0, 1.8 * scale]
        parts["neck_socket"] = self.create_socket(neck_location, 0.1 * scale, 0.1 * scale, self.tolerance)
        parts["neck_insert"] = self.create_insert(neck_location, 0.1 * scale, 0.12 * scale, self.tolerance)
        
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
