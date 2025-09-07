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
        self.character_type = "human"
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

    def create_socket(self, base_mesh, radius=0.1, depth=0.1, tolerance=-0.05):
        """Crear socket de encastre en una malla"""
        # Cilindro para el socket
        socket = trimesh.creation.cylinder(radius=radius, height=depth)
        
        # Aplicar tolerancia (más pequeño)
        socket.apply_scale(1 + abs(tolerance), 1 + abs(tolerance), 1)
        
        # Alinear al centro del objeto
        center = base_mesh.centroid
        socket.apply_translation(center)
        
        return socket

    def create_insert(self, location, radius=0.1, depth=0.12, tolerance=-0.05):
        """Crear inserto para encajar"""
        insert = trimesh.creation.cylinder(radius=radius + tolerance, height=depth)
        insert.apply_translation(location)
        return insert

    def subtract_part(self, base_mesh, part_to_subtract, offset=0.0):
        """Restar una parte de otra (corte)"""
        # Ajustar posición
        part_to_subtract.apply_translation([0, 0, offset])
        
        # Realizar operación booleana
        try:
            result = base_mesh.boolean_difference([part_to_subtract], operation='difference')
            return result
        except Exception as e:
            print(f"Error en corte: {e}")
            return base_mesh

    def generate_head_with_hair(self, head_path, hair_path, scale=1.0):
        """Generar cabeza con cabello y corte para encastre"""
        # Cargar modelos
        head = self.load_model(head_path)
        hair = self.load_model(hair_path)
        
        # Escalar
        head.apply_scale(scale)
        hair.apply_scale(scale)
        
        # Alinear posiciones
        hair.apply_translation([0, 0, 0.1 * scale])  # Ligeramente arriba
        
        # Cortar hueco en la cabeza para el pelo
        head_with_cut = self.subtract_part(head, hair, offset=0.01)
        
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
        eye_with_pupil = self.subtract_part(eye_white, pupil, offset=0.01)
        
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
        parts["neck_socket"] = self.create_socket(parts["head"], 0.1 * scale, 0.1 * scale, self.tolerance)
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