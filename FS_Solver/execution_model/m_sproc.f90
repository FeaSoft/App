! Description:
! Solution procedures.
module m_sproc
    use linear_algebra
    use data_model
    use m_gproc
    implicit none
    
    private
    public static_analysis
    
    contains
    
    ! Description:
    ! Performs a static analysis
    type(t_odb) function static_analysis(mdb) result(odb)
        ! procedure arguments
        type(t_mdb), intent(in) :: mdb ! model database
        
        ! additional variables
        type(t_sparse)              :: Kaa, Kab              ! global stiffness matrix
        type(t_vector)              :: Pa                    ! equivalent nodal loads vector
        type(t_vector)              :: Fe                    ! external nodal forces
        type(t_vector)              :: Ua                    ! unknown displacements
        type(t_vector)              :: Ub                    ! prescribed nodal displacements
        type(t_vector)              :: R                     ! reaction forces
        type(t_vector)              :: Fa, Fb                ! internal nodal forces
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
        call g_get_K(mdb%n_adofs, mdb%n_idofs, mdb%mesh, mdb%sections, mdb%materials, Kaa, Kab)
        
        ! compute equivalent nodal loads vector
        Pa = new_vector(mdb%n_adofs)
        call g_add_Pc(mdb%mesh%m_space, mdb%n_cloads, mdb%mesh%nodes, mdb%cloads, mdb%nsets, Pa) ! add concentrated loads
        
        ! add contribution from prescribed nodal displacements
        Ub = g_get_Ub(mdb%mesh%m_space, mdb%n_idofs, mdb%n_boundaries, mdb%mesh%nodes, mdb%boundaries, mdb%nsets)
        Fe = subtract(Pa, multiply(Kab, Ub))
        
        ! compute unknown displacements
        Ua = solve(Kaa, Fe)
        
        ! compute strain energy
        strain_energy = dot(Ua, Fe)/2.0
        
        ! compute reaction forces
        R = multiply(Kab, Ua, transposeA=.true.)
        
        ! compute internal nodal forces
        ! also computes strains and stresses at the integration points
        call g_get_F(mdb%n_adofs, mdb%n_idofs, mdb%mesh, mdb%sections, mdb%materials, Ua, Ub, Fa, Fb, strain_ips, stress_ips)
        
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
        
        ! create output database
        odb = new_odb(mdb%mesh%n_nodes, 3, 31)
        
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
        call odb%set_nsfout_descr( 9, 'Strain:Component XX of Strain'             )
        call odb%set_nsfout_descr(10, 'Strain:Component YY of Strain'             )
        call odb%set_nsfout_descr(11, 'Strain:Component ZZ of Strain'             )
        call odb%set_nsfout_descr(12, 'Strain:Component YZ of Strain'             )
        call odb%set_nsfout_descr(13, 'Strain:Component ZX of Strain'             )
        call odb%set_nsfout_descr(14, 'Strain:Component XY of Strain'             )
        call odb%set_nsfout_descr(15, 'Strain:Max. Principal Value of Strain'     )
        call odb%set_nsfout_descr(16, 'Strain:Mid. Principal Value of Strain'     )
        call odb%set_nsfout_descr(17, 'Strain:Min. Principal Value of Strain'     )
        call odb%set_nsfout_descr(18, 'Strain:Major Principal Value of Strain'    )
        call odb%set_nsfout_descr(19, 'Stress:Component XX of Stress'             )
        call odb%set_nsfout_descr(20, 'Stress:Component YY of Stress'             )
        call odb%set_nsfout_descr(21, 'Stress:Component ZZ of Stress'             )
        call odb%set_nsfout_descr(22, 'Stress:Component YZ of Stress'             )
        call odb%set_nsfout_descr(23, 'Stress:Component ZX of Stress'             )
        call odb%set_nsfout_descr(24, 'Stress:Component XY of Stress'             )
        call odb%set_nsfout_descr(25, 'Stress:Max. Principal Value of Stress'     )
        call odb%set_nsfout_descr(26, 'Stress:Mid. Principal Value of Stress'     )
        call odb%set_nsfout_descr(27, 'Stress:Min. Principal Value of Stress'     )
        call odb%set_nsfout_descr(28, 'Stress:Major Principal Value of Stress'    )
        call odb%set_nsfout_descr(29, 'Stress:Tresca Equivalent Stress'           )
        call odb%set_nsfout_descr(30, 'Stress:Mises Equivalent Stress'            )
        call odb%set_nsfout_descr(31, 'Stress:Equivalent Pressure Stress'         )
        
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
        call odb%set_nsfout(frame,  9, strain_extra_mesh%at(:,  1))
        call odb%set_nsfout(frame, 10, strain_extra_mesh%at(:,  2))
        call odb%set_nsfout(frame, 11, strain_extra_mesh%at(:,  3))
        call odb%set_nsfout(frame, 12, strain_extra_mesh%at(:,  4))
        call odb%set_nsfout(frame, 13, strain_extra_mesh%at(:,  5))
        call odb%set_nsfout(frame, 14, strain_extra_mesh%at(:,  6))
        call odb%set_nsfout(frame, 15, strain_extra_mesh%at(:,  7))
        call odb%set_nsfout(frame, 16, strain_extra_mesh%at(:,  8))
        call odb%set_nsfout(frame, 17, strain_extra_mesh%at(:,  9))
        call odb%set_nsfout(frame, 18, strain_extra_mesh%at(:, 10))
        call odb%set_nsfout(frame, 19, stress_extra_mesh%at(:,  1))
        call odb%set_nsfout(frame, 20, stress_extra_mesh%at(:,  2))
        call odb%set_nsfout(frame, 21, stress_extra_mesh%at(:,  3))
        call odb%set_nsfout(frame, 22, stress_extra_mesh%at(:,  4))
        call odb%set_nsfout(frame, 23, stress_extra_mesh%at(:,  5))
        call odb%set_nsfout(frame, 24, stress_extra_mesh%at(:,  6))
        call odb%set_nsfout(frame, 25, stress_extra_mesh%at(:,  7))
        call odb%set_nsfout(frame, 26, stress_extra_mesh%at(:,  8))
        call odb%set_nsfout(frame, 27, stress_extra_mesh%at(:,  9))
        call odb%set_nsfout(frame, 28, stress_extra_mesh%at(:, 10))
        call odb%set_nsfout(frame, 29, stress_extra_mesh%at(:, 11))
        call odb%set_nsfout(frame, 30, stress_extra_mesh%at(:, 12))
        call odb%set_nsfout(frame, 31, stress_extra_mesh%at(:, 13))
        
        ! squeeze storage
        call odb%squeeze()
    end function
    
end module
