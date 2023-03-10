! Description:
! Solver job input file reader.
module m_reader
    use data_model
    implicit none
    
    private
    public read_input
    
    ! error messages
    character(*), parameter :: ERROR_UNDEFINED_INPUT_SEQUENCE = 'Error: undefined input sequence'
    
    contains
    
    ! Description:
    ! Create a new finite element model database by reading the user-specified job input file.
    type(t_mdb) function read_input(file) result(mdb)
        character(*), intent(in) :: file ! solver job input file path
        
        ! reader helper variables
        character(64) :: command                                     ! current command being parsed
        character(3)  :: advance                                     ! reader advance flag
        integer       :: i, j, k                                     ! loop counters
        integer       :: ip1, ip2, ip3, ip4, ip5, ip6, ip7, ip8, ip9 ! integer parameters
        real          :: rp1, rp2, rp3                               ! real parameters
        logical       :: lp1, lp2, lp3                               ! logical parameters
        character     :: cp1                                         ! character parameters
        type(t_mesh)  :: mesh                                        ! finite element mesh
        
        ! open solver job input file for reading
        open(unit=1, action='read', file=file)
        
        ! parse: mesh
        read(unit=1, fmt=*) command; if (trim(command) /= 'mesh') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
        read(unit=1, fmt=*) ip1, ip2, ip3; mesh = new_mesh(ip1, ip2, ip3)
        
        ! parse: nodes
        read(unit=1, fmt=*) command; if (trim(command) /= 'nodes') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
        do i = 1, mesh%n_nodes
            read(unit=1, fmt=*) rp1, rp2, rp3; mesh%nodes(i) = new_node(mesh%m_space, rp1, rp2, rp3)
        end do
        
        ! parse: elements
        read(unit=1, fmt=*) command; if (trim(command) /= 'elements') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
        do i = 1, mesh%n_elements
            read(unit=1, fmt='(I,I)', advance='no') ip1, ip2; mesh%elements(i) = new_element(ip1, ip2)
            advance = 'no'
            do j = 1, mesh%elements(i)%n_nodes
                if (j == mesh%elements(i)%n_nodes) advance = 'yes'
                read(unit=1, fmt='(I)', advance=advance) mesh%elements(i)%i_nodes(j)
            end do
        end do
        
        ! parse: database
        read(unit=1, fmt=*) command; if (trim(command) /= 'database') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
        read(unit=1, fmt=*) ip1, ip2, ip3, ip4, ip5, ip6, ip7, ip8, ip9; mdb = new_mdb(ip1, ip2, ip3, ip4, ip5, ip6, ip7, ip8, ip9, mesh)
        
        ! parse: node-set
        do i = 1, mdb%n_nsets
            read(unit=1, fmt=*) command; if (trim(command) /= 'node-set') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
            read(unit=1, fmt=*) ip1; mdb%nsets(i) = new_nset(ip1)
            do j = 1, mdb%nsets(i)%n_nodes
                read(unit=1, fmt=*) mdb%nsets(i)%i_nodes(j)
            end do
        end do
        
        ! parse: element-set
        do i = 1, mdb%n_esets
            read(unit=1, fmt=*) command; if (trim(command) /= 'element-set') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
            read(unit=1, fmt=*) ip1; mdb%esets(i) = new_eset(ip1)
            do j = 1, mdb%esets(i)%n_elements
                read(unit=1, fmt=*) mdb%esets(i)%i_elements(j)
            end do
        end do
        
        ! parse: surface-set
        do i = 1, mdb%n_ssets
            read(unit=1, fmt=*) command; if (trim(command) /= 'surface-set') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
            read(unit=1, fmt=*) ip1; mdb%ssets(i) = new_sset(ip1)
            do j = 1, mdb%ssets(i)%n_surfaces
                read(unit=1, fmt='(I,I)', advance='no') ip1, ip2; mdb%ssets(i)%surfaces(j) = new_surface(ip1, ip2)
                advance = 'no'
                do k = 1, mdb%ssets(i)%surfaces(j)%n_nodes
                    if (k == mdb%ssets(i)%surfaces(j)%n_nodes) advance = 'yes'
                    read(unit=1, fmt='(I)', advance=advance) mdb%ssets(i)%surfaces(j)%i_nodes(k)
                end do
            end do
        end do
        
        ! parse: material
        do i = 1, mdb%n_materials
            read(unit=1, fmt=*) command; if (trim(command) /= 'material') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
            read(unit=1, fmt=*) rp1, rp2, rp3; mdb%materials(i) = new_material(rp1, rp2, rp3)
        end do
        
        ! parse: section
        do i = 1, mdb%n_sections
            read(unit=1, fmt=*) command; if (trim(command) /= 'section') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
            read(unit=1, fmt=*) ip1, ip2, ip3, rp1; mdb%sections(i) = new_section(mdb%mesh%m_space, ip1, ip2, ip3, rp1)
        end do
        
        ! parse: concentrated-load
        do i = 1, mdb%n_cloads
            read(unit=1, fmt=*) command; if (trim(command) /= 'concentrated-load') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
            read(unit=1, fmt=*) ip1, rp1, rp2, rp3; mdb%cloads(i) = new_cload(ip1, rp1, rp2, rp3)
        end do
        
        ! parse: surface-load
        do i = 1, mdb%n_sloads
            read(unit=1, fmt=*) command; if (trim(command) /= 'surface-load') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
            read(unit=1, fmt=*) ip1, cp1, rp1, rp2, rp3; mdb%sloads(i) = new_sload(ip1, cp1, rp1, rp2, rp3)
        end do
        
        ! parse: body-load
        do i = 1, mdb%n_bloads
            read(unit=1, fmt=*) command; if (trim(command) /= 'body-load') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
            read(unit=1, fmt=*) ip1, cp1, rp1, rp2, rp3; mdb%bloads(i) = new_bload(ip1, cp1, rp1, rp2, rp3)
        end do
        
        ! parse: boundary-condition
        do i = 1, mdb%n_boundaries
            read(unit=1, fmt=*) command; if (trim(command) /= 'boundary-condition') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
            read(unit=1, fmt=*) ip1, rp1, rp2, rp3, lp1, lp2, lp3; mdb%boundaries(i) = new_boundary(ip1, rp1, rp2, rp3, lp1, lp2, lp3)
        end do
        
        ! final actions
        call mdb%mesh%count_elements_per_node()
        
        ! close file
        close(unit=1)
    end function
    
end module
