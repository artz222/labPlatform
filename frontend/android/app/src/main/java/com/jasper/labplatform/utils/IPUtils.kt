package com.jasper.labplatform.utils

import android.content.Context
import android.util.Log
import android.view.LayoutInflater
import android.widget.EditText
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.jasper.labplatform.R

fun showIpInputDialog(context: Context, onSuccess: (ip: String) -> Unit) {
    val dialogView = LayoutInflater.from(context).inflate(R.layout.dialog_ip_input, null)
    val ipEditText = dialogView.findViewById<EditText>(R.id.ip_edit_text)

    MaterialAlertDialogBuilder(context)
        .setTitle("Connect to Server")
        .setView(dialogView) // Set the custom view
        .setPositiveButton("Submit") { dialog, which ->
            val enteredIp = ipEditText.text.toString()
            if (isValidIpAddress(enteredIp)) {
                Log.i("IpDialog", "Submitted IP Address: $enteredIp")
                onSuccess(enteredIp)
            } else {
                // Optionally, show an error to the user or keep the dialog open
                Log.w("IpDialog", "Invalid IP Address entered: $enteredIp")
                ipEditText.error = "Invalid IP Address"
                // Note: For more complex validation or to prevent dialog closing on invalid input,
                // you might need to override the button's OnClickListener after the dialog is shown.
            }
        }
        .setNegativeButton("Cancel") { dialog, which ->
            dialog.dismiss()
        }
        .setCancelable(false) // Optional: Prevent dismissing by tapping outside or back press
        .show()
}

fun isValidIpAddress(ip: String): Boolean {
    // Basic IP address validation (you can use a more robust regex or library)
    // This is a simple check, Android's Patterns.IP_ADDRESS is more thorough
    // if you add it as a dependency or copy the regex.
    val ipRegex =
        """^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"""
    return ip.matches(Regex(ipRegex))
    // For a more robust solution, consider using Android's built-in Patterns:
    // return android.util.Patterns.IP_ADDRESS.matcher(ip).matches()
}