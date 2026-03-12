using UnityEngine;
using TMPro; // Important: This allows the script to talk to TextMeshPro
using UnityEngine.SceneManagement; // Added this at the top!


public class GameManager : MonoBehaviour
{
    // This 'instance' allows other scripts (like the Star) to find the GameManager easily
    public static GameManager instance;

    public bool isGameActive = false;


    [Header("Game Settings")]
    public float timeLeft = 60f;
    public int score = 0;

    [Header("UI Elements")]
    public TMP_Text timerText;
    public TMP_Text scoreText;

    [Header("Victory UI")]
    public GameObject victoryPanel;
    public TMP_Text finalScoreText;

    void Awake()
    {
        // Set up the singleton instance
        if (instance == null) instance = this;
    }

    void Update()
    {

        if (isGameActive) // Only run the game if this is true
        {
            if (timeLeft > 0)
            {
                timeLeft -= Time.deltaTime;
                UpdateUI();
            }
            else
            {
                timeLeft = 0;
                UpdateUI();
                GameOver();
            }
        }

        if (Input.GetKeyDown(KeyCode.Escape))
        {
            // Toggle the menu or just quit
            QuitGame(); 
        }
        
    }

    public void StartGame()
    {
        isGameActive = true;
        GameObject.Find("StartMenu").SetActive(false); // Hides the menu
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
    }

    public void AddScore(int points)
    {
        score += points;
        UpdateUI();
    }

    void UpdateUI()
    {
        // Mathf.Ceil turns 59.7 into 60 so the timer looks clean
        if (timerText != null) timerText.text = "Time: " + Mathf.Ceil(timeLeft).ToString();
        if (scoreText != null) scoreText.text = "Points: " + score.ToString();
    }

    void GameOver()
    {
        Debug.Log("Game Over! You collected " + score + " stars.");
        // You can add code here to freeze the boat or show a 'Restart' button later
        isGameActive = false;
        victoryPanel.SetActive(true);
        finalScoreText.text = "Your Score: " + score;
        
        // Unlock the mouse cursor so you can click the button
        Cursor.lockState = CursorLockMode.None;
        Cursor.visible = true;
    }
    public void RestartGame()
    {
        victoryPanel.SetActive(false);
        // Reloads the current scene
        SceneManager.LoadScene(SceneManager.GetActiveScene().name);
    }
    public void QuitGame()
    {
        Debug.Log("Quit Button Pressed!"); // This confirms it works in the console
        Application.Quit(); // This closes the actual game window
    }
}