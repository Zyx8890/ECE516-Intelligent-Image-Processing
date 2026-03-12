using UnityEngine;

public class BoatController : MonoBehaviour
{
    [Header("Movement Settings")]
    public float maxSpeed = 20f;
    public float acceleration = 5f;   // How fast it reaches max speed
    public float deceleration = 3f;   // How fast it drifts to a stop
    
    [Header("Turning Settings")]
    public float maxTurnSpeed = 100f;
    public float turnSensitivity = 50f; // How "heavy" the steering feels
    public float maxTiltAngle = 20f; // Max degrees to lean
    public float tiltSmoothness = 5f; // How "heavy" the boat feels
    private float currentTilt = 0f;
    private Rigidbody rb;
    private float currentSpeedInput = 0f;
    private float currentTurnInput = 0f;

    void Start() => rb = GetComponent<Rigidbody>();

    void FixedUpdate()
    {
        if (GameManager.instance != null && !GameManager.instance.isGameActive) return;

        // 1. Get Raw Input (-1, 0, or 1)
        float targetMove = Input.GetAxisRaw("Vertical");
        float targetTurn = Input.GetAxisRaw("Horizontal");

        // 2. Linear Acceleration/Deceleration Logic
        float moveStep = (targetMove != 0) ? acceleration : deceleration;
        currentSpeedInput = Mathf.MoveTowards(currentSpeedInput, targetMove, moveStep * Time.fixedDeltaTime);

        // 3. Smooth Turning Logic
        currentTurnInput = Mathf.MoveTowards(currentTurnInput, targetTurn, turnSensitivity * Time.fixedDeltaTime);

        // Apply Movement
        rb.AddRelativeForce(Vector3.forward * currentSpeedInput * maxSpeed * rb.mass);

        // Apply Rotation
        float turn = currentTurnInput * maxTurnSpeed * Time.fixedDeltaTime;
        rb.MoveRotation(rb.rotation * Quaternion.Euler(0, turn, 0));

        float targetTilt = -currentTurnInput * maxTiltAngle;
        currentTilt = Mathf.Lerp(currentTilt, targetTilt, Time.deltaTime * tiltSmoothness);

    }
}