package com.jasper.labplatform.view

import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.Window
import android.widget.ImageButton
import androidx.annotation.RequiresApi
import androidx.core.graphics.drawable.toDrawable
import androidx.core.net.toUri
import androidx.core.view.WindowInsetsCompat
import androidx.fragment.app.DialogFragment
import com.bumptech.glide.Glide
import com.github.chrisbanes.photoview.PhotoView
import com.jasper.labplatform.R

class ImageZoomDialogFragment : DialogFragment() {

    private lateinit var photoView: PhotoView
    private lateinit var closeButton: ImageButton

    companion object {
        private const val ARG_IMAGE_URL = "image_url"
        private const val ARG_IMAGE_URI = "image_uri" // For local images

        fun newInstance(
            imageUrl: String? = null,
            imageUri: String? = null
        ): ImageZoomDialogFragment {
            val fragment = ImageZoomDialogFragment()
            val args = Bundle()
            imageUrl?.let { args.putString(ARG_IMAGE_URL, it) }
            imageUri?.let { args.putString(ARG_IMAGE_URI, it) }
            fragment.arguments = args
            return fragment
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        // Inflate the layout for this fragment
        val view = inflater.inflate(R.layout.dialog_full_screen_image, container, false)

        // Optional: Make the dialog background transparent
        dialog?.window?.setBackgroundDrawable(Color.TRANSPARENT.toDrawable())
        // Optional: Remove title
        dialog?.window?.requestFeature(Window.FEATURE_NO_TITLE)

        return view
    }

    @RequiresApi(Build.VERSION_CODES.R)
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        photoView = view.findViewById(R.id.dialog_photo_view)
        closeButton = view.findViewById(R.id.close_button)

        val imageUrl = arguments?.getString(ARG_IMAGE_URL)
        val imageUriString = arguments?.getString(ARG_IMAGE_URI)

        if (imageUrl != null) {
            Glide.with(this)
                .load(imageUrl)
                .into(photoView)
        } else if (imageUriString != null) {
            Glide.with(this)
                .load(imageUriString.toUri())
                .into(photoView)
        } else {
            // Handle error or show placeholder
            // photoView.setImageResource(R.drawable.error_image) // Example
            dismiss() // Or show an error message in the dialog
        }

        closeButton.setOnClickListener {
            dismiss()
        }
        // 隐藏导航栏
        dialog?.window?.let {
            hideNavBar(it)
        }
    }

    @RequiresApi(Build.VERSION_CODES.R)
    override fun onStart() {
        super.onStart()
        // Make the dialog full-screen
        dialog?.window?.setLayout(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        )
    }
}

@RequiresApi(Build.VERSION_CODES.R)
fun hideNavBar(window: Window) {
    window.insetsController?.hide(WindowInsetsCompat.Type.navigationBars())
}