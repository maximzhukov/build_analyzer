from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseVolumeStrategy(ABC):
    @abstractmethod
    def calculate_volume(self, detected_objects: List[Dict[str, Any]], current_volume: float) -> float:
        pass


class EarthworkStrategy(BaseVolumeStrategy):
    def calculate_volume(self, detected_objects: List[Dict[str, Any]], current_volume: float) -> float:
        trucks = [obj for obj in detected_objects if obj.get("class") == "dump_truck"]
        volume_per_truck = 15.0  
        added_volume = len(trucks) * volume_per_truck
        return current_volume + added_volume


class BrickworkStrategy(BaseVolumeStrategy):
    def calculate_volume(self, detected_objects: List[Dict[str, Any]], current_volume: float) -> float:
        pallets = [obj for obj in detected_objects if obj.get("class") == "pallet_brick"]
        volume_per_pallet = 2.5  
        added_volume = len(pallets) * volume_per_pallet
        return current_volume + added_volume


class DefaultStrategy(BaseVolumeStrategy):
    def calculate_volume(self, detected_objects: List[Dict[str, Any]], current_volume: float) -> float:
        return current_volume


class StrategyRegistry:
    _strategies = {
        "STAGE_EARTH_WORK": EarthworkStrategy(),
        "STAGE_BRICK_WORK": BrickworkStrategy(),
    }
    
    @classmethod
    def get_strategy(cls, nlp_stage_id: str) -> BaseVolumeStrategy:
        return cls._strategies.get(nlp_stage_id, DefaultStrategy())