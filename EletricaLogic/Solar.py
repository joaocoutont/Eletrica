# Estimador Solar Fotovoltaico Completo (ABSOLAR / INMET)
import math
import FreeCAD

# ... (HSP_BRASIL, PANEL_POWERS, INVERTERS permanecem iguais)

class SolarEstimator:
    # ... (métodos existentes permanecem iguais)

    @staticmethod
    def simplified_shadow_analysis(panel_obj, obstacles):
        """
        Analisa o impacto de sombreamento usando intersecção geométrica.
        Projeta um sólido 'sombra' na direção oposta ao sol e verifica colisões.
        """
        if not panel_obj or not obstacles:
            return 1.0 
            
        import Part
        # Vetor Sol simplificado (Médio para Brasil: Elevação 45°, Azimute Norte/180°)
        # Coordenadas: Z+ (Cima), Y+ (Norte)
        sun_vec = FreeCAD.Vector(0, 1, 1).normalize()
        
        # Cria uma linha de teste (raio) a partir do centro do painel
        p_center = panel_obj.Shape.CenterOfMass
        ray_end = p_center + (sun_vec * 10000.0) # 10 metros de raio
        ray = Part.makeLine(p_center, ray_end)
        
        shadow_hits = 0
        for obs in obstacles:
            if not hasattr(obs, "Shape") or not obs.Shape: continue
            if obs.Name == panel_obj.Name: continue
            
            # Verifica intersecção real entre o raio do sol e o obstáculo
            inter = ray.intersect(obs.Shape)
            if inter:
                shadow_hits += 1
                
        # Perda estimada: 20% por objeto bloqueador detectado
        loss = max(0.2, 1.0 - (shadow_hits * 0.20))
        return loss

    @staticmethod
    def estimate_with_3d_data(panel_obj):
        """Estima a geração lendo a área do objeto 3D e analisando sombras locais."""
        doc = FreeCAD.ActiveDocument
        if not panel_obj: return None
        
        # 1. Obter Área Real do painel no 3D
        area = panel_obj.Shape.Area / 1e6 if hasattr(panel_obj, "Shape") else 2.0 # m2
        
        # 2. Análise de Sombras
        others = [obj for obj in doc.Objects if obj.Name != panel_obj.Name]
        sf = SolarEstimator.simplified_shadow_analysis(panel_obj, others)
        
        # 3. Cálculo base (Assume 550Wp para cada 2.5m2)
        wp_est = (area / 2.5) * 550.0
        
        # 4. Resultado com perdas de sombreamento
        res = SolarEstimator.estimate_pv_system(monthly_kwh=300, efficiency=0.80 * sf)
        res["fator_sombreamento"] = sf
        res["potencia_3d_wp"] = round(wp_est, 2)
        
        return res
