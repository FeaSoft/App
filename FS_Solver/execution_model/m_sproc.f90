! Description:
! Solution procedures.
module m_sproc
    use m_constants
    use linear_algebra
    use data_model
    use m_gproc
    implicit none
    
    private
    public static_analysis, frequency_analysis, buckle_analysis
    
    contains
    
    ! Description:
    ! Performs a static analysis
    type(t_odb) function static_analysis(mdb) result(odb)
        ! procedure arguments
        type(t_mdb), intent(in) :: mdb ! model database
        
        ! additional variables
        type(t_sparse)              :: Kaa, Kab, Kba, Kbb    ! global stiffness matrix
        type(t_vector)              :: Pa                    ! equivalent nodal loads vector
        type(t_vector)              :: Fe                    ! external nodal forces
        type(t_vector)              :: Ua                    ! unknown displacements
        type(t_vector)              :: Ub                    ! prescribed nodal displacements
        type(t_vector)              :: R                     ! reaction forces
        type(t_vector)              :: Fa                    ! internal nodal forces
        type(t_matrix), allocatable :: strain_ips(:)         ! strain at the integration points (basic components)
        type(t_matrix), allocatable :: stress_ips(:)         ! stress at the integration points (basic components
        type(t_matrix), allocatable :: strain_nodes(:)       ! strain at the element nodes (basic components)
        type(t_matrix), allocatable :: stress_nodes(:)       ! stress at the element nodes (basic components)
        type(t_matrix), allocatable :: strain_extra_nodes(:) ! strain at the element nodes (basic components + extra measures)
        type(t_matrix), allocatable :: stress_extra_nodes(:) ! stress at the element nodes (basic components + extra measures)
        type(t_matrix)              :: strain_extra_mesh     ! strain at the mesh nodes (basic components + extra measures)
        type(t_matrix)              :: stress_extra_mesh     ! stress at the mesh nodes (basic components + extra measures)
        type(t_matrix)              :: displacement          ! displacements at the mesh nodes
        type(t_matrix)              :: reaction              ! reaction forces at the mesh nodes
        type(t_matrix)              :: nodal_load            ! equivalent nodal loads at the mesh nodes
        real                        :: strain_energy         ! strain energy
        real                        :: residual              ! residual (infinity norm of the out-of-balance forces vector)
        integer                     :: frame                 ! current output frame
        
        ! allocate storage
        allocate(strain_ips(mdb%mesh%n_elements))
        allocate(stress_ips(mdb%mesh%n_elements))
        allocate(strain_nodes(mdb%mesh%n_elements))
        allocate(stress_nodes(mdb%mesh%n_elements))
        allocate(strain_extra_nodes(mdb%mesh%n_elements))
        allocate(stress_extra_nodes(mdb%mesh%n_elements))
        
        ! compute global stiffness matrix
        call g_get_K(mdb%n_adofs, mdb%n_idofs, mdb%mesh, mdb%sections, mdb%materials, Kaa, Kab, Kba, Kbb)
        
        ! compute equivalent nodal loads vector
        Pa = new_vector(mdb%n_adofs)
        call g_add_Pc(mdb%mesh%m_space, mdb%n_cloads, mdb%mesh%nodes, mdb%cloads, mdb%nsets, Pa)                   ! add concentrated loads
        call g_add_Ps(mdb%n_adofs, mdb%n_sloads, mdb%mesh, mdb%sloads, mdb%ssets, mdb%sections, Pa)                ! add surface loads
        call g_add_Pb(mdb%n_adofs, mdb%n_bloads, mdb%mesh, mdb%bloads, mdb%esets, mdb%sections, mdb%materials, Pa) ! add body loads
        
        ! add contribution from prescribed nodal displacements
        Ub = g_get_Ub(mdb%mesh%m_space, mdb%n_idofs, mdb%n_boundaries, mdb%mesh%nodes, mdb%boundaries, mdb%nsets)
        Fe = subtract(Pa, multiply(Kab, Ub))
        
        ! compute unknown displacements
        Ua = solve(Kaa, Fe)
        
        ! compute strain energy
        strain_energy = dot(Ua, Fe)/2.0
        
        ! compute reaction forces
        R = add(multiply(Kba, Ua), multiply(Kbb, Ub))
        
        ! compute internal nodal forces
        ! also computes strains and stresses at the integration points
        call g_get_F(mdb%n_adofs, mdb%mesh, mdb%sections, mdb%materials, Ua, Ub, Fa, strain_ips, stress_ips)
        
        ! compute residual
        residual = maxabs(subtract(Fe, Fa))
        
        ! perform extrapolation from element integration points to element nodes
        ! deallocate unused storage
        call extrapolate(mdb%mesh%n_elements, mdb%mesh%elements, strain_ips, strain_nodes); if (allocated(strain_ips)) deallocate(strain_ips)
        call extrapolate(mdb%mesh%n_elements, mdb%mesh%elements, stress_ips, stress_nodes); if (allocated(stress_ips)) deallocate(stress_ips)
        
        ! compute additional strain and stress measures (principal strains, principal stresses, and equivalent stresses)
        ! deallocate unused storage
        call extra_strain(strain_nodes, strain_extra_nodes); if (allocated(strain_nodes)) deallocate(strain_nodes)
        call extra_stress(stress_nodes, stress_extra_nodes); if (allocated(stress_nodes)) deallocate(stress_nodes)
        
        ! compute values at mesh nodes (perform final smoothing)
        strain_extra_mesh = average(mdb%mesh, strain_extra_nodes, 10); if (allocated(strain_extra_nodes)) deallocate(strain_extra_nodes)
        stress_extra_mesh = average(mdb%mesh, stress_extra_nodes, 13); if (allocated(stress_extra_nodes)) deallocate(stress_extra_nodes)
        
        ! convert global vectors to result matrices
        displacement = convert_vector(mdb%mesh%m_space, mdb%mesh%n_nodes, mdb%mesh%nodes, Ua, Ub)
        reaction     = convert_vector(mdb%mesh%m_space, mdb%mesh%n_nodes, mdb%mesh%nodes, new_vector(mdb%n_adofs), R)
        nodal_load   = convert_vector(mdb%mesh%m_space, mdb%mesh%n_nodes, mdb%mesh%nodes, Pa, new_vector(mdb%n_idofs))
        
        ! create output database
        odb = new_odb(mdb%mesh%n_nodes, 3, 35)
        
        ! history output descriptions
        call odb%set_hout_descr(1, 'Time')
        call odb%set_hout_descr(2, 'Residual')
        call odb%set_hout_descr(3, 'Strain Energy')
        
        ! nodal scalar field output descriptions
        call odb%set_nsfout_descr( 1, 'Displacement:Displacement in X'            )
        call odb%set_nsfout_descr( 2, 'Displacement:Displacement in Y'            )
        call odb%set_nsfout_descr( 3, 'Displacement:Displacement in Z'            )
        call odb%set_nsfout_descr( 4, 'Displacement:Magnitude of Displacement'    )
        call odb%set_nsfout_descr( 5, 'Reaction Force:Reaction Force in X'        )
        call odb%set_nsfout_descr( 6, 'Reaction Force:Reaction Force in Y'        )
        call odb%set_nsfout_descr( 7, 'Reaction Force:Reaction Force in Z'        )
        call odb%set_nsfout_descr( 8, 'Reaction Force:Magnitude of Reaction Force')
        call odb%set_nsfout_descr( 9, 'Nodal Load:Nodal Load in X'                )
        call odb%set_nsfout_descr(10, 'Nodal Load:Nodal Load in Y'                )
        call odb%set_nsfout_descr(11, 'Nodal Load:Nodal Load in Z'                )
        call odb%set_nsfout_descr(12, 'Nodal Load:Magnitude of Nodal Load'        )
        call odb%set_nsfout_descr(13, 'Strain:Component XX of Strain'             )
        call odb%set_nsfout_descr(14, 'Strain:Component YY of Strain'             )
        call odb%set_nsfout_descr(15, 'Strain:Component ZZ of Strain'             )
        call odb%set_nsfout_descr(16, 'Strain:Component YZ of Strain'             )
        call odb%set_nsfout_descr(17, 'Strain:Component ZX of Strain'             )
        call odb%set_nsfout_descr(18, 'Strain:Component XY of Strain'             )
        call odb%set_nsfout_descr(19, 'Strain:Max. Principal Value of Strain'     )
        call odb%set_nsfout_descr(20, 'Strain:Mid. Principal Value of Strain'     )
        call odb%set_nsfout_descr(21, 'Strain:Min. Principal Value of Strain'     )
        call odb%set_nsfout_descr(22, 'Strain:Major Principal Value of Strain'    )
        call odb%set_nsfout_descr(23, 'Stress:Component XX of Stress'             )
        call odb%set_nsfout_descr(24, 'Stress:Component YY of Stress'             )
        call odb%set_nsfout_descr(25, 'Stress:Component ZZ of Stress'             )
        call odb%set_nsfout_descr(26, 'Stress:Component YZ of Stress'             )
        call odb%set_nsfout_descr(27, 'Stress:Component ZX of Stress'             )
        call odb%set_nsfout_descr(28, 'Stress:Component XY of Stress'             )
        call odb%set_nsfout_descr(29, 'Stress:Max. Principal Value of Stress'     )
        call odb%set_nsfout_descr(30, 'Stress:Mid. Principal Value of Stress'     )
        call odb%set_nsfout_descr(31, 'Stress:Min. Principal Value of Stress'     )
        call odb%set_nsfout_descr(32, 'Stress:Major Principal Value of Stress'    )
        call odb%set_nsfout_descr(33, 'Stress:Tresca Equivalent Stress'           )
        call odb%set_nsfout_descr(34, 'Stress:Mises Equivalent Stress'            )
        call odb%set_nsfout_descr(35, 'Stress:Equivalent Pressure Stress'         )
        
        ! create output frame
        frame = odb%new_frame('Increment: 1, Time: 1.0')
        
        ! history output
        call odb%set_hout(frame, 1, 1.0)
        call odb%set_hout(frame, 2, residual)
        call odb%set_hout(frame, 3, strain_energy)
        
        ! nodal scalar field output
        call odb%set_nsfout(frame,  1,      displacement%at(:,  1))
        call odb%set_nsfout(frame,  2,      displacement%at(:,  2))
        call odb%set_nsfout(frame,  3,      displacement%at(:,  3))
        call odb%set_nsfout(frame,  4,      displacement%at(:,  4))
        call odb%set_nsfout(frame,  5,          reaction%at(:,  1))
        call odb%set_nsfout(frame,  6,          reaction%at(:,  2))
        call odb%set_nsfout(frame,  7,          reaction%at(:,  3))
        call odb%set_nsfout(frame,  8,          reaction%at(:,  4))
        call odb%set_nsfout(frame,  9,        nodal_load%at(:,  1))
        call odb%set_nsfout(frame, 10,        nodal_load%at(:,  2))
        call odb%set_nsfout(frame, 11,        nodal_load%at(:,  3))
        call odb%set_nsfout(frame, 12,        nodal_load%at(:,  4))
        call odb%set_nsfout(frame, 13, strain_extra_mesh%at(:,  1))
        call odb%set_nsfout(frame, 14, strain_extra_mesh%at(:,  2))
        call odb%set_nsfout(frame, 15, strain_extra_mesh%at(:,  3))
        call odb%set_nsfout(frame, 16, strain_extra_mesh%at(:,  4))
        call odb%set_nsfout(frame, 17, strain_extra_mesh%at(:,  5))
        call odb%set_nsfout(frame, 18, strain_extra_mesh%at(:,  6))
        call odb%set_nsfout(frame, 19, strain_extra_mesh%at(:,  7))
        call odb%set_nsfout(frame, 20, strain_extra_mesh%at(:,  8))
        call odb%set_nsfout(frame, 21, strain_extra_mesh%at(:,  9))
        call odb%set_nsfout(frame, 22, strain_extra_mesh%at(:, 10))
        call odb%set_nsfout(frame, 23, stress_extra_mesh%at(:,  1))
        call odb%set_nsfout(frame, 24, stress_extra_mesh%at(:,  2))
        call odb%set_nsfout(frame, 25, stress_extra_mesh%at(:,  3))
        call odb%set_nsfout(frame, 26, stress_extra_mesh%at(:,  4))
        call odb%set_nsfout(frame, 27, stress_extra_mesh%at(:,  5))
        call odb%set_nsfout(frame, 28, stress_extra_mesh%at(:,  6))
        call odb%set_nsfout(frame, 29, stress_extra_mesh%at(:,  7))
        call odb%set_nsfout(frame, 30, stress_extra_mesh%at(:,  8))
        call odb%set_nsfout(frame, 31, stress_extra_mesh%at(:,  9))
        call odb%set_nsfout(frame, 32, stress_extra_mesh%at(:, 10))
        call odb%set_nsfout(frame, 33, stress_extra_mesh%at(:, 11))
        call odb%set_nsfout(frame, 34, stress_extra_mesh%at(:, 12))
        call odb%set_nsfout(frame, 35, stress_extra_mesh%at(:, 13))
        
        ! squeeze storage
        call odb%squeeze()
    end function
    
    ! Description:
    ! Performs a frequency analysis
    type(t_odb) function frequency_analysis(mdb, k0) result(odb)
        ! procedure arguments
        type(t_mdb), intent(in) :: mdb ! model database
        integer,     intent(in) :: k0  ! requested number of eigenpairs
        
        ! additional variables
        type(t_sparse) :: Kaa, Kab, Kba, Kbb ! global stiffness matrix
        type(t_sparse) :: Maa, Mab, Mba, Mbb ! global mass matrix
        type(t_vector) :: E                  ! eigenvalues
        type(t_matrix) :: X                  ! eigenvectors
        type(t_vector) :: f                  ! natural frequencies
        type(t_vector) :: phi                ! eigenvector
        type(t_matrix) :: displacement       ! displacements at the mesh nodes
        real           :: norm               ! norm with respect to mass matrix
        integer        :: k                  ! number of eigenpairs found
        integer        :: i                  ! loop counter
        integer        :: frame              ! current output frame
        character(64)  :: frame_descr        ! frame description
        
        ! compute global stiffness matrix
        call g_get_K(mdb%n_adofs, mdb%n_idofs, mdb%mesh, mdb%sections, mdb%materials, Kaa, Kab, Kba, Kbb)
        
        ! compute global mass matrix
        call g_get_M(mdb%n_adofs, mdb%n_idofs, mdb%mesh, mdb%sections, mdb%materials, Maa, Mab, Mba, Mbb)
        
        ! solve generalized sparse eigenproblem
        call eigen('S', Kaa, Maa, k0, k, E, X)
        
        ! compute frequencies
        f = new_vector(E%n_vals)
        f%at(:) = sqrt(E%at(:))/(2.0*PI)
        
        ! normalize eigenvectors
        do i = 1, k
            phi = new_vector(mdb%n_adofs)
            phi%at(:) = X%at(:, i)
            norm = sqrt(dot(phi, multiply(Maa, phi)))
            X%at(:, i) = phi%at(:)/norm
        end do
        
        ! create output database
        odb = new_odb(mdb%mesh%n_nodes, 2, 4)
        
        ! history output descriptions
        call odb%set_hout_descr(1, 'Eigenvalue')
        call odb%set_hout_descr(2, 'Frequency' )
        
        ! nodal scalar field output descriptions
        call odb%set_nsfout_descr(1, 'Displacement:Displacement in X'        )
        call odb%set_nsfout_descr(2, 'Displacement:Displacement in Y'        )
        call odb%set_nsfout_descr(3, 'Displacement:Displacement in Z'        )
        call odb%set_nsfout_descr(4, 'Displacement:Magnitude of Displacement')
        
        ! loop frames
        do i = 1, k
            ! create output frame
            write(frame_descr, '("Mode: ",I0,", Value: ",SP,E12.5,", Frequency: ",E12.5)') i, E%at(i), f%at(i)
            frame = odb%new_frame(frame_descr)
            
            ! history output
            call odb%set_hout(frame, 1, E%at(i))
            call odb%set_hout(frame, 2, f%at(i))
            
            ! nodal scalar field output
            phi = new_vector(mdb%n_adofs)
            phi%at(:) = X%at(:, i)
            displacement = convert_vector(mdb%mesh%m_space, mdb%mesh%n_nodes, mdb%mesh%nodes, phi, new_vector(mdb%n_idofs))
            call odb%set_nsfout(frame, 1, displacement%at(:, 1))
            call odb%set_nsfout(frame, 2, displacement%at(:, 2))
            call odb%set_nsfout(frame, 3, displacement%at(:, 3))
            call odb%set_nsfout(frame, 4, displacement%at(:, 4))
        end do
        
        ! squeeze storage
        call odb%squeeze()
    end function
    
    ! Description:
    ! Performs a buckle analysis
    type(t_odb) function buckle_analysis(mdb, k0) result(odb)
        ! procedure arguments
        type(t_mdb), intent(in) :: mdb ! model database
        integer,     intent(in) :: k0  ! requested number of eigenpairs
        
        ! additional variables
        type(t_sparse) :: Kaa, Kab, Kba, Kbb ! global stiffness matrix
        type(t_sparse) :: Saa, Sab, Sba, Sbb ! global stress-stiffness matrix
        type(t_vector) :: Pa                 ! equivalent nodal loads vector
        type(t_vector) :: Fe                 ! external nodal forces
        type(t_vector) :: Ua                 ! unknown displacements
        type(t_vector) :: Ub                 ! prescribed nodal displacements
        type(t_vector) :: E                  ! eigenvalues
        type(t_matrix) :: X                  ! eigenvectors
        type(t_vector) :: phi                ! eigenvector
        type(t_matrix) :: displacement       ! displacements at the mesh nodes
        real           :: norm               ! eigenvector infinity norm
        integer        :: k                  ! number of eigenpairs found
        integer        :: i                  ! loop counter
        integer        :: frame              ! current output frame
        character(64)  :: frame_descr        ! frame description
        
        ! ---------------------------------------
        ! step 1. perform a static analysis
        ! ---------------------------------------
        
        ! compute global stiffness matrix
        call g_get_K(mdb%n_adofs, mdb%n_idofs, mdb%mesh, mdb%sections, mdb%materials, Kaa, Kab, Kba, Kbb)
        
        ! compute equivalent nodal loads vector
        Pa = new_vector(mdb%n_adofs)
        call g_add_Pc(mdb%mesh%m_space, mdb%n_cloads, mdb%mesh%nodes, mdb%cloads, mdb%nsets, Pa)                   ! add concentrated loads
        call g_add_Ps(mdb%n_adofs, mdb%n_sloads, mdb%mesh, mdb%sloads, mdb%ssets, mdb%sections, Pa)                ! add surface loads
        call g_add_Pb(mdb%n_adofs, mdb%n_bloads, mdb%mesh, mdb%bloads, mdb%esets, mdb%sections, mdb%materials, Pa) ! add body loads
        
        ! add contribution from prescribed nodal displacements
        Ub = g_get_Ub(mdb%mesh%m_space, mdb%n_idofs, mdb%n_boundaries, mdb%mesh%nodes, mdb%boundaries, mdb%nsets)
        Fe = subtract(Pa, multiply(Kab, Ub))
        
        ! compute unknown displacements
        Ua = solve(Kaa, Fe)
        
        ! ---------------------------------------
        ! step 2. solve the eigenproblem
        ! ---------------------------------------
        
        ! compute global stress-stiffness matrix
        call g_get_S(mdb%n_adofs, mdb%n_idofs, mdb%mesh, mdb%sections, mdb%materials, Ua, Ub, Saa, Sab, Sba, Sbb)
        
        ! solve generalized sparse eigenproblem
        call eigen('S', Saa, Kaa, k0, k, E, X)
        
        ! general post-processing
        do i = 1, k
            ! get eigenvalue
            E%at(i) = 1.0/E%at(i)
            
            ! normalize vector
            phi = new_vector(mdb%n_adofs)
            phi%at(:) = X%at(:, i)
            norm = maxabs(phi)
            X%at(:, i) = X%at(:, i)/norm
        end do
        
        ! create output database
        odb = new_odb(mdb%mesh%n_nodes, 2, 4)
        
        ! history output descriptions
        call odb%set_hout_descr(1, 'Eigenvalue')
        call odb%set_hout_descr(2, 'Critical Load Magnitude')
        
        ! nodal scalar field output descriptions
        call odb%set_nsfout_descr(1, 'Displacement:Displacement in X'        )
        call odb%set_nsfout_descr(2, 'Displacement:Displacement in Y'        )
        call odb%set_nsfout_descr(3, 'Displacement:Displacement in Z'        )
        call odb%set_nsfout_descr(4, 'Displacement:Magnitude of Displacement')
        
        ! loop frames
        do i = 1, k
            ! create output frame
            write(frame_descr, '("Mode: ",I0,", Value: ",SP,E12.5,", Magnitude: ",E12.5)') i, E%at(i), -E%at(i)
            frame = odb%new_frame(frame_descr)
            
            ! history output
            call odb%set_hout(frame, 1, +E%at(i))
            call odb%set_hout(frame, 2, -E%at(i))
            
            ! nodal scalar field output
            phi = new_vector(mdb%n_adofs)
            phi%at(:) = X%at(:, i)
            displacement = convert_vector(mdb%mesh%m_space, mdb%mesh%n_nodes, mdb%mesh%nodes, phi, new_vector(mdb%n_idofs))
            call odb%set_nsfout(frame, 1, displacement%at(:, 1))
            call odb%set_nsfout(frame, 2, displacement%at(:, 2))
            call odb%set_nsfout(frame, 3, displacement%at(:, 3))
            call odb%set_nsfout(frame, 4, displacement%at(:, 4))
        end do
        
        ! squeeze storage
        call odb%squeeze()
    end function
    
end module
