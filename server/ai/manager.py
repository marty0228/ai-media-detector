from ai.visual_anomaly.predict import load_model as load_m1, predict as predict_m1
from ai.external_search.predict import load_model as load_m2, predict as predict_m2
from ai.forensic_analysis.predict import load_model as load_m3, predict as predict_m3
from ai.meta_data.predict import load_model as load_m4, predict as predict_m4
from ai.water_mark.predict import load_model as load_m5, predict as predict_m5
from ai.ansbel_model.predict import load_model as load_meta, predict as predict_meta

def load_ai_model():
    """
    Load all 5 base AI models and the meta-regression model.
    """
    print("Loading all AI models...")
    load_m1()
    load_m2()
    load_m3()
    load_m4()
    load_m5()
    load_meta()
    print("All AI models loaded successfully.")

def predict_all(image_bytes: bytes) -> dict:
    """
    Pass the image to all 5 models, collect their results,
    and then pass those results to the meta-model to get the final output.
    """
    try:
        # Get predictions from the 5 base models
        res1 = predict_m1(image_bytes)
        res2 = predict_m2(image_bytes)
        res3 = predict_m3(image_bytes)
        res4 = predict_m4(image_bytes)
        res5 = predict_m5(image_bytes)
        
        individual_results = [res1, res2, res3, res4, res5]
        
        # Pass base results to the meta-model
        final_result = predict_meta(individual_results)
        
        # Combine everything to be sent to the client
        return {
            "final_prediction": final_result,
            "individual_predictions": individual_results
        }
        
    except Exception as e:
        print(f"Error during unified prediction workflow: {e}")
        return {
            "error": str(e)
        }
