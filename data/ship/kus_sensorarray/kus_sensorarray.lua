if GLOBAL_LIB_IMPORTED == nil or GLOBAL_LIB_IMPORTED == 0 then
    dofilepath("data:scripts/playerspatch/playerspatch_ships_util.lua")
    GLOBAL_LIB_IMPORTED = 1
end
function Update_Kus_SensorArray(CustomGroup, playerIndex, shipID)	
	if Player_GetLevelOfDifficulty(playerIndex) > 0 and Player_GetNumberOfSquadronsOfTypeAwakeOrSleeping(-1, "Special_Splitter" ) == 1 then	
		if SobGroup_Empty("kus_mothership"..playerIndex) == 0 then 	
			SobGroup_ParadeSobGroup(CustomGroup, "kus_mothership"..playerIndex, 0)	
		elseif SobGroup_Empty("kus_carrier"..playerIndex) == 0 then
			SobGroup_ParadeSobGroup(CustomGroup, "kus_carrier"..playerIndex, 0)	
		end		
	end	
	
	SobGroup_NoSalvageScuttle(CustomGroup, playerIndex, shipID)
end

function NKR_SensorUpdate(group, playerIndex, shipID)
    local enabled = Player_HasResearch(playerIndex, "NKR_HyperspaceSensors")
    SobGroup_SetHardPointHealth(group, "NKR Hyperspace Sensor", enabled)
    Update_Kus_SensorArray(group, playerIndex, shipID)
end
