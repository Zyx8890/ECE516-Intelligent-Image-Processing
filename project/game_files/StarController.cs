using UnityEngine;

public class Star : MonoBehaviour
{
    [Header("Animation")]
    public float rotationSpeed = 100f;

    void Update()
    {
        // Make the star spin so it looks like a collectible
        transform.Rotate(Vector3.up * rotationSpeed * Time.deltaTime);
    }

    // This runs when another object enters the "Trigger" zone
    void OnTriggerEnter(Collider other)
    {
        // Check if the thing that hit us is the Player
        if (other.CompareTag("Player"))
        {
            // Update the score in the GameManager
            if (GameManager.instance != null)
            {
                GameManager.instance.AddScore(1);
            }

            // Optional: Play a sound effect here!
            
            // Remove the star from the game
            Destroy(gameObject);
        }
    }
}